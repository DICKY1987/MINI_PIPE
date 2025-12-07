"""
Phase 1 Integration Example - DiffStats Usage
"""

from src.minipipe.patch_converter import PatchConverter, DiffStats

# Sample unified diff
sample_diff = """
--- a/src/auth.py
+++ b/src/auth.py
@@ -1,5 +1,7 @@
 def authenticate(user):
-    if user.password == hash:
+    # Use bcrypt instead
+    if bcrypt.check(user.password):
         return True
+    return False
"""

# Create converter and compute stats
converter = PatchConverter()
stats = converter.compute_diff_stats(sample_diff)

print(f"✅ DiffStats working!")
print(f"   {stats}")
