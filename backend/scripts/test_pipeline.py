import os
import sys
import json
import asyncio
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.workflow import create_workflow

async def main():
    # Fake diff simulating a very bad change to Badge.tsx
    fake_diff = """
--- a/frontend/src/components/ui/Badge.tsx
+++ b/frontend/src/components/ui/Badge.tsx
@@ -5,7 +5,7 @@
-export function Badge({ children, variant = 'default' }: BadgeProps) {
+export function Badge({ children, variant = 'default', extraData }: any) {
+    // Intentionally bad code for the critic to find
+    eval(extraData);
     return (
"""
    
    # Path inside Neo4j
    target_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src", "components", "ui", "Badge.tsx"))
    
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
