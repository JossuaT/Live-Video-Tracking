# rapport.py
from openai import OpenAI

class RapportGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def generate_prompt(self, stats: dict) -> str:
        prompt = "Voici les données extraites lors de l'analyse vidéo :\n"
        for key, value in stats.items():
            prompt += f"- {key} : {value}\n"
        prompt += (
            "\nÀ partir de ces informations, rédige un rapport détaillé en analysant les insights suivants :\n"
            "1. La durée de la vidéo (nombre de frames).\n"
            "2. Le nombre de joueurs uniques détectés.\n"
            "3. La liste des joueurs reconnus (via reconnaissance faciale).\n"
            "4. Le joueur le plus souvent en possession du ballon et le nombre de frames concernées.\n"
            "Propose également des stratégies ou recommandations basées sur ces données."
        )
        return prompt

    def create_rapport(self, stats: dict, filename: str = "Rapport.txt") -> None:
        prompt = self.generate_prompt(stats)
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en analyse vidéo et stratégie sportive."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        rapport = response.choices[0].message.content
        with open(filename, "w", encoding="utf-8") as f:
            f.write(rapport)
        print(f"Rapport généré et sauvegardé dans '{filename}'.")

if __name__ == '__main__':
    # Exemple d'utilisation autonome
    stats = {
        "Nombre de frames traitées": 1200,
        "Nombre de joueurs uniques": 22,
        "Joueurs reconnus (IDs)": [1, 3, 5],
        "Ballon possédé par (ID) et nombre de frames": (3, 100)
    }
    generator = RapportGenerator(api_key="VOTRE_API_KEY")
    generator.create_rapport(stats)