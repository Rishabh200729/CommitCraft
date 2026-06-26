import os
import sys
import json
import asyncio
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.workflow import create_workflow

async def main():
    # Fake diff simulating insecure payment credentials
    fake_diff = """
--- a/frontend/src/components/PaymentForm.tsx
+++ b/frontend/src/components/PaymentForm.tsx
@@ -10,7 +10,10 @@
   const handleSubmit = (e: React.FormEvent) => {
     e.preventDefault();
-    submitToGateway({ cardNumber, cvc });
+    // Hardcoded encryption key for debugging
+    const key = "DEBUG_SECRET_KEY_12345";
+    const encrypted = encryptPayload({ cardNumber, cvc }, key);
+    submitToGateway(encrypted);
   };
 """
    
    # Path inside Neo4j
    target_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src", "components", "PaymentForm.tsx"))
    
    app = create_workflow()
    
    print("Starting LangGraph Execution...")
    
    initial_state = {
        "target_file": target_file,
        "pr_diff": fake_diff
    }
    
    result = await app.ainvoke(initial_state)
    
    print("\n--- FINAL VERDICT JSON ---")
    print(json.dumps(result.get("final_verdict", {}), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
