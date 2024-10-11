import requests
import json

# Inserisci qui l'ID utente di Discord che vuoi testare
USER_ID = "ID UTENTE"  # Sostituisci con l'ID utente reale

def simulate_frontend_click():
    url = "http://localhost:8080/confirm"
    payload = {"user_id": USER_ID}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print(f"Conferma inviata con successo per l'utente {USER_ID}")
            print("Risposta del server:", response.json())
        else:
            print(f"Errore nell'invio della conferma. Codice di stato: {response.status_code}")
            print("Risposta del server:", response.text)
    except requests.RequestException as e:
        print(f"Errore nella richiesta: {e}")

if __name__ == "__main__":
    simulate_frontend_click()
