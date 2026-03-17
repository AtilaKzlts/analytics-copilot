from agent.agent import run_agent

sorular = [
    "Satışçılarda gelir anomalisi var mı?",
    "Hangi satışçı çok uzun sürede deal kapatıyor?",
    "Pipeline'da anomali var mı?",
]

for soru in sorular:
    print(f"\nSORU: {soru}")
    print("-" * 50)
    print(run_agent(soru))