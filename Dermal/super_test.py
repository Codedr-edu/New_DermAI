import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input as eff_preprocess
from tensorflow.keras.layers import Conv2D, DepthwiseConv2D, SeparableConv2D
from PIL import Image
import io
import os
import base64
import matplotlib.cm as cm
import time
import traceback

# ------------------------------
# Config
# ------------------------------
MODEL_PATH = os.path.join(os.path.dirname(
    __file__), "dermatology_stage1.keras")
IMG_SIZE_DEFAULT = 300

CLASS_NAMES = [
    "Acne and Rosacea Photos",
    "Eczema Photos",
    "Heathy",
    "Psoriasis pictures Lichen Planus and related diseases",
    "Scabies Lyme Disease and other Infestations and Bites",
    "Seborrheic Keratoses and other Benign Tumors",
    "Warts Molluscum and other Viral Infections",
]

# ------------------------------
# Load model safely and wrap
# ------------------------------
print("🔄 Loading model from:", MODEL_PATH)
_loaded_model = keras.models.load_model(MODEL_PATH, compile=False)
print("Loaded model:", type(_loaded_model),
      "name:", getattr(_loaded_model, "name", None))

# infer input size if possible
try:
    in_shape = _loaded_model.inputs[0].shape.as_list()
    if in_shape and in_shape[1] and in_shape[2]:
        IMG_SIZE = int(in_shape[1])
    else:
        IMG_SIZE = IMG_SIZE_DEFAULT
except Exception:
    IMG_SIZE = IMG_SIZE_DEFAULT
print("Using IMG_SIZE =", IMG_SIZE)

# try to build model by calling on a zero tensor (float32)
try:
    dummy = tf.zeros((1, IMG_SIZE, IMG_SIZE, 3), dtype=tf.float32)
    _ = _loaded_model(dummy, training=False)
    print("✅ _loaded_model called successfully on dummy tensor (built).")
except Exception as e:
    print("⚠️ calling _loaded_model(dummy) failed:", e)

# Try to create a functional wrapper that uses a fresh Input tensor.
"""
WRAPPED_MODEL = None
try:
    inp = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3),
                      dtype=tf.float32, name="gradcam_input")
    out = _loaded_model(inp, training=False)
    WRAPPED_MODEL = keras.Model(inputs=inp, outputs=out)
    print("✅ WRAPPED_MODEL created (functional wrapper).")
except Exception as e:
    print("⚠️ Could not create functional wrapper directly:", e)
    WRAPPED_MODEL = None
"""
WRAPPED_MODEL = keras.Model(
    inputs=_loaded_model.input,
    outputs=_loaded_model.output
)
print("✅ WRAPPED_MODEL created (uses original model input).")
print("WRAPPED_MODEL.inputs:", WRAPPED_MODEL.inputs)

# If wrapper didn't build, attempt to force-build by calling _loaded_model
# with candidate preprocesses (so that internal submodels get built), then wrap.


def try_force_build_and_wrap(np_example):
    global WRAPPED_MODEL
    if WRAPPED_MODEL is not None:
        return True
    # preprocessing candidates (same logic as later)
    candidates = []
    arr = np_example.astype("float32")
    try:
        candidates.append(("efficientnet_preprocess", np.expand_dims(
            eff_preprocess(arr.copy()).astype("float32"), axis=0)))
    except Exception:
        pass
    try:
        candidates.append(("div255", np.expand_dims(
            (arr/255.0).astype("float32"), axis=0)))
    except Exception:
        pass
    try:
        candidates.append(
            ("raw_float32", np.expand_dims(arr.astype("float32"), axis=0)))
    except Exception:
        pass

    for name, batch in candidates:
        try:
            _ = _loaded_model(tf.convert_to_tensor(batch), training=False)
            # now try wrapping
            inp = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3),
                              dtype=tf.float32, name="gradcam_input")
            out = _loaded_model(inp, training=False)
            WRAPPED_MODEL = keras.Model(inputs=inp, outputs=out)
            print(
                f"✅ Built WRAPPED_MODEL by forcing _loaded_model with candidate preprocess '{name}'")
            return True
        except Exception as e:
            print(f"  - forcing with {name} failed: {repr(e)}")
    return False

# ------------------------------
# Utility: find last conv layer (recursive)
# ------------------------------


def find_last_conv_layer_recursive(model):
    """
    Return the last Conv-like layer object (Conv2D / Depthwise / Separable) found
    by recursively traversing model.layers. Return None if none found.
    """
    last_conv = None
    try:
        layers_iter = getattr(model, "layers", []) or []
    except Exception:
        layers_iter = []
    for layer in layers_iter:
        # If it's a Model/Submodel or Sequential, recurse
        if isinstance(layer, tf.keras.Model) or isinstance(layer, keras.Sequential):
            sub = find_last_conv_layer_recursive(layer)
            if sub is not None:
                last_conv = sub
        elif isinstance(layer, (Conv2D, DepthwiseConv2D, SeparableConv2D)):
            last_conv = layer
    return last_conv

# ------------------------------
# Preprocess candidates (yield name, batch_np)
# ------------------------------


def pil_to_np(img_pil, img_size):
    img = img_pil.resize((img_size, img_size), Image.LANCZOS)
    arr = np.array(img)
    return arr


def candidate_preprocessors(np_img):
    """
    yields (name, batch_np (1,H,W,3) float32)
    order: eff_preprocess, /255, raw float32
    """
    arr = np_img.astype("float32")
    # EfficientNetV2 preprocess
    try:
        a = eff_preprocess(arr.copy()).astype("float32")
        yield "efficientnet_v2_preprocess_input", np.expand_dims(a, axis=0)
    except Exception:
        pass
    # div255
    try:
        b = (arr / 255.0).astype("float32")
        yield "div255", np.expand_dims(b, axis=0)
    except Exception:
        pass
    # raw float32
    try:
        c = arr.astype("float32")
        yield "raw_uint8_float32", np.expand_dims(c, axis=0)
    except Exception:
        pass

# ------------------------------
# Grad-CAM compute (uses layer object)
# ------------------------------


def compute_gradcam_for_batch(batch_np, wrapped_model, last_conv_layer, pred_index=None):
    """
    batch_np: numpy array shape (1,H,W,3) float32 (already preprocessed appropriate to model).
    last_conv_layer: layer object (not string)
    """
    # ensure input is float32 tensor
    x = tf.convert_to_tensor(batch_np, dtype=tf.float32)
    # ensure the model graph is built with this input
    _ = wrapped_model(x, training=False)

    # create grad model that outputs conv feature map and final preds
    grad_model = keras.models.Model(inputs=wrapped_model.input, outputs=[
                                    last_conv_layer.output, wrapped_model.output])

    # _ = grad_model(x, training=False)
    # conv_model = grad_model({"gradcam_input": x}, training=False)

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(x, training=False)
        # choose prediction index
        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    # grads of class wrt conv_outputs
    grads = tape.gradient(class_channel, conv_outputs)
    # global-average pool grads
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]  # HxWxC
    # weighted combination
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-10)
    return heatmap.numpy(), predictions.numpy()

# ------------------------------
# High-level predict + heatmap (robust)
# ------------------------------


def predict_skin_with_explanation(image_bytes, top_k=7):
    """
    Returns (results_list, heatmap_base64_or_None)
    results_list: list of dicts {"class": name, "probability": percent}
    """
    start_time = time.time()
    pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    np_img = pil_to_np(pil, IMG_SIZE)

    # ensure WRAPPED_MODEL exists (try to force-build and wrap)
    global WRAPPED_MODEL
    if WRAPPED_MODEL is None:
        ok = try_force_build_and_wrap(np_img)
        if not ok:
            # last resort: try to use _loaded_model as wrapper (may still work)
            WRAPPED_MODEL = _loaded_model
            print("⚠️ Using _loaded_model directly as WRAPPED_MODEL (best-effort).")

    # find last conv layer inside WRAPPED_MODEL
    last_conv_layer = find_last_conv_layer_recursive(WRAPPED_MODEL)
    if last_conv_layer is None:
        print(
            "⚠️ No Conv-like layer found in model. Will return predictions without heatmap.")
    else:
        print("🔍 last_conv_layer.name =", last_conv_layer.name)

    # try candidate preprocessors and pick first that runs
    chosen_method = None
    chosen_batch = None
    preds = None
    for name, batch in candidate_preprocessors(np_img):
        try:
            # convert and forward
            batch_t = tf.convert_to_tensor(batch, dtype=tf.float32)
            out = WRAPPED_MODEL(batch_t, training=False)
            preds = out.numpy()
            chosen_method = name
            chosen_batch = batch
            print(f"✅ Preprocess '{name}' works; preds shape {preds.shape}")
            break
        except Exception as e:
            print(f"  preprocess '{name}' failed: {e}")

    if chosen_method is None:
        raise RuntimeError(
            "All preprocessing attempts failed; cannot run model on example.")

    # build results list
    preds_vect = preds[0]
    results = [
        {"class": (CLASS_NAMES[i] if i < len(CLASS_NAMES) else f"class_{i}"),
         "probability": float(preds_vect[i]) * 100}
        for i in range(len(preds_vect))
    ]
    results = sorted(results, key=lambda x: x["probability"], reverse=True)[
        :top_k]

    # compute heatmap if possible
    heatmap_base64 = None
    if last_conv_layer is not None:
        try:
            heatmap, _ = compute_gradcam_for_batch(
                chosen_batch, WRAPPED_MODEL, last_conv_layer)
            # overlay on original (resized)
            original_img = pil.resize((IMG_SIZE, IMG_SIZE))
            img_array = np.array(original_img)

            heatmap_img = np.uint8(255 * heatmap)
            heatmap_img = Image.fromarray(heatmap_img).resize(
                (img_array.shape[1], img_array.shape[0]), Image.BILINEAR)
            heatmap_arr = np.array(heatmap_img)

            colormap = cm.get_cmap("jet")
            colored_heatmap = np.uint8(255 * colormap(heatmap_arr)[:, :, :3])

            superimposed = Image.blend(original_img.convert("RGBA"),
                                       Image.fromarray(
                                           colored_heatmap).convert("RGBA"),
                                       alpha=0.4)
            buf = io.BytesIO()
            superimposed.save(buf, format="PNG")
            heatmap_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception as e:
            print("⚠️ Failed to compute Grad-CAM:",
                  repr(e), traceback.format_exc())
            heatmap_base64 = None

    elapsed = time.time() - start_time
    print(
        f"⏱️ Done in {elapsed:.2f}s. Preprocess used: {chosen_method}. Heatmap produced: {heatmap_base64 is not None}")
    return results, heatmap_base64

# ------------------------------
# Simple predict wrapper
# ------------------------------


def predict_skin_simple(image_bytes, top_k=7):
    res, _ = predict_skin_with_explanation(image_bytes, top_k=top_k)
    return res
