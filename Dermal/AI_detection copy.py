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

print("🔄 Loading model from:", MODEL_PATH)
_loaded_model = keras.models.load_model(MODEL_PATH, compile=False)
print("✅ Loaded model:", type(_loaded_model),
      "name:", getattr(_loaded_model, "name", None))

# Extract input info
try:
    orig_input_tensor = _loaded_model.inputs[0]
    orig_dtype = orig_input_tensor.dtype
    orig_shape = orig_input_tensor.shape.as_list()[1:]
    print(f"Model input info: shape={orig_shape}, dtype={orig_dtype}")
except Exception as e:
    print(f"⚠️ Error extracting input info: {e}")
    orig_shape = [IMG_SIZE_DEFAULT, IMG_SIZE_DEFAULT, 3]
    orig_dtype = tf.float32

IMG_SIZE = orig_shape[0] if orig_shape[0] else IMG_SIZE_DEFAULT

WRAPPED_MODEL = _loaded_model

# Warm up the model
dummy_input = tf.zeros((1,) + tuple(orig_shape), dtype=orig_dtype)
_ = WRAPPED_MODEL(dummy_input, training=False)
print("✅ Model warmed up")


def pil_to_np(img_pil, img_size):
    """Convert PIL image to numpy array"""
    img = img_pil.resize((img_size, img_size), Image.LANCZOS)
    return np.array(img)


def candidate_preprocessors(np_img, target_dtype):
    """Generate different preprocessing candidates"""
    arr = np_img.astype(np.float32)

    # EfficientNetV2 preprocessing
    try:
        processed = eff_preprocess(arr.copy()).astype(np.float32)
        if hasattr(target_dtype, 'as_numpy_dtype'):
            if target_dtype.as_numpy_dtype == np.float16:
                processed = processed.astype(np.float16)
        yield "efficientnet_v2_preprocess", np.expand_dims(processed, axis=0)
    except Exception as e:
        print(f"  ⚠️ efficientnet_v2_preprocess failed: {e}")

    # Simple normalization
    try:
        processed = (arr / 255.0).astype(np.float32)
        if hasattr(target_dtype, 'as_numpy_dtype'):
            if target_dtype.as_numpy_dtype == np.float16:
                processed = processed.astype(np.float16)
        yield "div255", np.expand_dims(processed, axis=0)
    except Exception as e:
        print(f"  ⚠️ div255 failed: {e}")


def find_target_layer_for_gradcam(model):
    """
    Find suitable layer for Grad-CAM in EfficientNet models.
    Returns layer name (string) instead of layer object.
    """
    target_layer_name = None

    def search_layers(m, path=""):
        nonlocal target_layer_name
        for layer in m.layers:
            layer_path = f"{path}/{layer.name}" if path else layer.name

            # Look for conv layers
            if isinstance(layer, (Conv2D, DepthwiseConv2D, SeparableConv2D)):
                target_layer_name = layer.name
                print(f"  🔍 Found conv: {layer_path}")

            # Recursively search nested models
            if isinstance(layer, tf.keras.Model):
                search_layers(layer, layer_path)

    search_layers(model)

    # For EfficientNet, also check for specific layer names
    if target_layer_name is None:
        for layer in model.layers:
            if 'top_conv' in layer.name or 'block7' in layer.name or 'block6' in layer.name:
                target_layer_name = layer.name
                print(f"  🔍 Using EfficientNet layer: {layer.name}")
                break

    return target_layer_name


def get_layer_by_name(model, layer_name):
    """Recursively find a layer by name in model (including nested models)"""
    for layer in model.layers:
        if layer.name == layer_name:
            return layer
        if isinstance(layer, tf.keras.Model):
            found = get_layer_by_name(layer, layer_name)
            if found is not None:
                return found
    return None


def compute_gradcam_manual(batch_np, model, target_layer_name, pred_index=None):
    """
    Compute Grad-CAM by getting the target layer and creating a sub-model
    """
    model_input_dtype = model.inputs[0].dtype
    print(f"  🔍 Model expects dtype: {model_input_dtype}")
    print(f"  🔍 Batch dtype: {batch_np.dtype}")

    # Convert to tensor
    x = tf.convert_to_tensor(batch_np, dtype=model_input_dtype)

    # Find the target layer recursively
    target_layer = get_layer_by_name(model, target_layer_name)

    if target_layer is None:
        raise RuntimeError(
            f"Could not find layer '{target_layer_name}' in model")

    print(
        f"  ✅ Found target layer: {target_layer.name} (type: {type(target_layer).__name__})")

    # Strategy: Create a custom forward pass that captures the target layer output
    try:
        with tf.GradientTape(persistent=True) as tape:
            tape.watch(x)

            # We'll manually trace through and capture when we hit our target layer
            conv_outputs = None

            # Custom call that watches for our target layer
            class ActivationCapture(tf.keras.layers.Layer):
                def __init__(self):
                    super().__init__()
                    self.captured = None

                def call(self, inputs):
                    self.captured = inputs
                    return inputs

            capture_layer = ActivationCapture()

            # Monkey-patch the target layer temporarily to capture its output
            original_call = target_layer.call

            def wrapped_call(inputs, *args, **kwargs):
                output = original_call(inputs, *args, **kwargs)
                nonlocal conv_outputs
                conv_outputs = output
                return output

            # Temporarily replace the call method
            target_layer.call = wrapped_call

            try:
                # Do forward pass
                predictions = model(x, training=False)

                if conv_outputs is None:
                    raise RuntimeError(
                        f"Failed to capture output from {target_layer_name}")

                print(f"  ✅ Captured conv output: {conv_outputs.shape}")
                print(f"  🔍 Predictions shape: {predictions.shape}")

            finally:
                # Restore original call method
                target_layer.call = original_call

            # Get target class
            if pred_index is None:
                pred_index = tf.argmax(predictions[0])

            class_channel = predictions[:, pred_index]
            print(
                f"  🔍 Target class: {pred_index.numpy()}, score: {class_channel.numpy()[0]:.4f}")

        # Compute gradients
        grads = tape.gradient(class_channel, conv_outputs)
        del tape  # Clean up persistent tape

        if grads is None:
            raise RuntimeError("Gradients are None!")

        print(f"  🔍 Gradients shape: {grads.shape}")
        print(
            f"  🔍 Gradients range: [{tf.reduce_min(grads).numpy():.4f}, {tf.reduce_max(grads).numpy():.4f}]")

        # Compute heatmap
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs_squeezed = conv_outputs[0]
        heatmap = conv_outputs_squeezed @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        print(
            f"  🔍 Raw heatmap range: [{tf.reduce_min(heatmap).numpy():.4f}, {tf.reduce_max(heatmap).numpy():.4f}]")

        # ReLU + normalize
        heatmap = tf.maximum(heatmap, 0)
        heatmap_max = tf.reduce_max(heatmap)

        if heatmap_max > 1e-10:
            heatmap = heatmap / heatmap_max
            print(f"  ✅ Normalized (max: {heatmap_max.numpy():.4f})")
        else:
            print(
                f"  ⚠️ Heatmap max too small: {heatmap_max.numpy():.6f}, using absolute values")
            heatmap = tf.abs(heatmap)
            heatmap_max = tf.reduce_max(heatmap)
            if heatmap_max > 1e-10:
                heatmap = heatmap / heatmap_max

        return heatmap.numpy(), predictions.numpy()

    except Exception as e:
        print(f"  ❌ Grad-CAM computation failed: {e}")
        traceback.print_exc()
        raise


def predict_skin_with_explanation(image_bytes, top_k=7):
    """
    Predict skin condition with Grad-CAM explanation
    """
    start_time = time.time()

    # Load image
    with Image.open(io.BytesIO(image_bytes)) as pil:
        pil = pil.convert("RGB")
        np_img = pil_to_np(pil, IMG_SIZE)

    # Find target layer
    print("🔍 Searching for target layer...")
    target_layer_name = find_target_layer_for_gradcam(WRAPPED_MODEL)

    if target_layer_name is None:
        print("❌ No suitable layer found for Grad-CAM!")
    else:
        print(f"✅ Target layer: {target_layer_name}")

    # Preprocess
    chosen_method = None
    chosen_batch = None
    preds = None

    for name, batch in candidate_preprocessors(np_img, WRAPPED_MODEL.inputs[0].dtype):
        try:
            preds = WRAPPED_MODEL(batch, training=False).numpy()
            chosen_method = name
            chosen_batch = batch
            print(f"✅ Preprocessing '{name}' works")
            break
        except Exception as e:
            print(f"  ❌ '{name}' failed: {e}")

    if preds is None:
        raise RuntimeError("All preprocessing failed")

    # Format results
    preds_vect = preds[0]
    results = [
        {
            "class": (CLASS_NAMES[i] if i < len(CLASS_NAMES) else f"class_{i}"),
            "probability": float(preds_vect[i]) * 100,
        }
        for i in range(len(preds_vect))
    ]
    results = sorted(results, key=lambda x: x["probability"], reverse=True)[
        :top_k]

    print(
        f"\n📊 Top prediction: {results[0]['class']} ({results[0]['probability']:.2f}%)")

    # Generate Grad-CAM
    heatmap_base64 = None
    if target_layer_name is not None:
        try:
            print("\n🔥 Computing Grad-CAM...")
            heatmap, _ = compute_gradcam_manual(
                chosen_batch, WRAPPED_MODEL, target_layer_name
            )

            print(f"  🔍 Heatmap shape: {heatmap.shape}")
            print(
                f"  🔍 Heatmap range: [{heatmap.min():.4f}, {heatmap.max():.4f}]")

            # Create visualization
            original_img = pil.resize((IMG_SIZE, IMG_SIZE))

            # Resize heatmap
            heatmap_uint8 = np.uint8(255 * heatmap)
            heatmap_img = Image.fromarray(heatmap_uint8).resize(
                (IMG_SIZE, IMG_SIZE), Image.BILINEAR
            )
            heatmap_arr = np.array(heatmap_img) / 255.0

            # Apply colormap
            colormap = cm.get_cmap("jet")
            colored_heatmap = colormap(heatmap_arr)[:, :, :3]
            colored_heatmap_uint8 = np.uint8(255 * colored_heatmap)

            # Blend
            superimposed = Image.blend(
                original_img.convert("RGBA"),
                Image.fromarray(colored_heatmap_uint8).convert("RGBA"),
                alpha=0.4,
            )

            # Encode
            buf = io.BytesIO()
            superimposed.save(buf, format="PNG")
            heatmap_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            print("✅ Grad-CAM generated!")

        except Exception as e:
            print(f"❌ Grad-CAM failed: {e}")
            traceback.print_exc()
            heatmap_base64 = None

    elapsed = time.time() - start_time
    print(
        f"\n⏱️ Time: {elapsed:.2f}s | Method: {chosen_method} | Heatmap: {'✅' if heatmap_base64 else '❌'}\n")

    return results, heatmap_base64


def predict_skin_simple(image_bytes, top_k=7):
    """Simple prediction without explanation"""
    res, _ = predict_skin_with_explanation(image_bytes, top_k=top_k)
    return res
