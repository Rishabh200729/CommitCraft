import os
import sys
import json
import asyncio
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.judge import judge_node

def main():
    print("Testing Judge Agent Hallucination Filtering...")
    
    # Mock state with hallucinated dependencies
    # The Senior Engineer hallucinated that PaymentGatewayService and UserAuth were affected.
    state = {
        "architectural_summary": "This change updates the Header component and heavily modifies the PaymentGatewayService and UserAuth DB schemas.",
        "risk_assessment": "High risk due to PaymentGatewayService changes.",
        "critic_flaws": ["Potential SQL injection in UserAuth."],
        "blast_radius": {
            "upstream": [],
            "downstream": [{"file": "frontend/src/components/Header.tsx"}]
        }
    }
    
    result = judge_node(state)
    
    print("\n--- FINAL VERDICT JSON ---")
    print(json.dumps(result.get("final_verdict", {}), indent=2))

if __name__ == "__main__":
    main()
