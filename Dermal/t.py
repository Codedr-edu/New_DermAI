import tensorflow as tf
from tensorflow import keras
import os

MODEL_PATH = "dermatology_stage1.keras"  # sửa nếu cần

print("🔄 Load model...")
loaded_model = keras.models.load_model(MODEL_PATH, compile=False)
print("✅ Loaded:", type(loaded_model), "name:",
      getattr(loaded_model, "name", None))

# 1) ép build bằng dummy input
try:
    dummy = tf.zeros((1, 300, 300, 3), dtype=tf.float32)
    _ = loaded_model(dummy, training=False)
    print("✅ Model accepted dummy input.")
except Exception as e:
    print("❌ Model cannot accept dummy input:", e)

# 2) thử wrap lại thành functional model
try:
    inp = keras.Input(shape=(300, 300, 3), name="gradcam_input")
    out = loaded_model(inp, training=False)
    wrapped_model = keras.Model(inputs=inp, outputs=out)
    print("✅ Wrapped model created successfully!")
    print("wrapped_model.inputs:", wrapped_model.inputs)
    print("wrapped_model.outputs:", wrapped_model.outputs)
except Exception as e:
    print("❌ Wrapping failed:", repr(e))

# 3) test predict
try:
    test_out = wrapped_model(dummy, training=False)
    print("✅ Wrapped model works on dummy, output shape =", test_out.shape)
except Exception as e:
    print("❌ Wrapped model cannot run:", e)
