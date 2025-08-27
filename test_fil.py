#!/usr/bin/env python3
# test_fil.py
# Test ICPC-2 RAG-systemet med notater fra fil

import os
import json
import sys
from rag_infer import infer

def test_from_file(filename):
    """Test systemet med notater fra en fil"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            note_text = f.read().strip()
        
        print(f"📖 Leser notat fra: {filename}")
        print(f"📏 Lengde: {len(note_text)} tegn")
        print("-" * 50)
        
        # Bruk streaming uten visuell output for fil-basert testing
        result = infer(note_text, stream=True, show_stream=False)
        
        print("✅ Resultat:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return result
        
    except FileNotFoundError:
        print(f"❌ Fil ikke funnet: {filename}")
        return None
    except Exception as e:
        print(f"❌ Feil: {e}")
        return None

def create_sample_file():
    """Opprett en eksempel-fil"""
    sample_content = """Anamnese: 45-årig kvinne med hodepine i 3 dager. 
Smerter er pulserende, lokalisert til høyre side av hodet. 
Ingen aura, ingen kvalme eller lysømfintlighet.

Status: Pasienten er orientert og samarbeidsvillig. 
Neurologisk status normal. 
Blodtrykk 140/85 mmHg.

Vurdering/Plan: Trolig spenningshodepine. 
Foreslår paracetamol 1g 4 ganger daglig ved behov. 
Kontroll om 1 uke hvis ikke bedring."""
    
    filename = "eksempel_notat.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"📝 Opprettet eksempel-fil: {filename}")
    return filename

def main():
    print("🏥 ICPC-2 RAG Test System (Fil-basert)")
    print("=" * 50)
    
    # Sett API-nøkkel
    api_key = input("Skriv inn din Mistral API-nøkkel (eller trykk Enter hvis allerede satt): ").strip()
    if api_key:
        os.environ["MISTRAL_API_KEY"] = api_key
    
    if len(sys.argv) > 1:
        # Bruk fil som kommandolinje-argument
        filename = sys.argv[1]
        test_from_file(filename)
    else:
        # Interaktiv modus
        print("\nVelg alternativ:")
        print("1. Test med eksempel-fil")
        print("2. Opprett ny eksempel-fil")
        print("3. Angi filnavn manuelt")
        
        choice = input("\nVelg (1-3): ").strip()
        
        if choice == "1":
            if os.path.exists("eksempel_notat.txt"):
                test_from_file("eksempel_notat.txt")
            else:
                print("❌ Eksempel-fil ikke funnet. Oppretter ny...")
                filename = create_sample_file()
                test_from_file(filename)
        
        elif choice == "2":
            filename = create_sample_file()
            test_from_file(filename)
        
        elif choice == "3":
            filename = input("Skriv filnavn: ").strip()
            test_from_file(filename)
        
        else:
            print("❌ Ugyldig valg")

if __name__ == "__main__":
    main()
