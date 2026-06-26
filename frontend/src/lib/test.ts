const diff = `diff --git a/frontend/src/components/PaymentForm.tsx b/frontend/src/components/PaymentForm.tsx
index 1234567..89abcd 100644
--- a/frontend/src/components/PaymentForm.tsx
+++ b/frontend/src/components/PaymentForm.tsx
@@ -1,5 +1,6 @@
 import React from 'react';
 import { Button } from './ui/Button';
+import { encryptPayload } from '../lib/crypto';
 
 export function PaymentForm() {
+  const handleSubmit = (e: any) => {
+    e.preventDefault();
+    // Hardcoded encryption key for debugging
+    const key = "DEBUG_SECRET_KEY_12345";
+    const encrypted = encryptPayload({ card: "1234" }, key);
+    console.log(encrypted);
+  };
   return (
-    <form>
+    <form onSubmit={handleSubmit}>
       <input type="text" placeholder="Card Number" />
       <Button variant="primary">Submit Payment</Button>
     </form>
diff --git a/frontend/src/lib/crypto.ts b/frontend/src/lib/crypto.ts
new file mode 100644
index 0000000..9999999
--- /dev/null
+++ b/frontend/src/lib/crypto.ts
@@ -0,0 +1,5 @@
+export function encryptPayload(data: any, key: string) {
+  // Insecure encryption logic for testing
+  console.log("Encrypting with key:", key);
+  return btoa(JSON.stringify(data));
+}
`;
export { diff };