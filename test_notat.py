#!/usr/bin/env python3
# test_notat.py
# Interaktiv test av ICPC-2 RAG-systemet

import os
import json
from rag_infer import infer

def main():
    print("🏥 ICPC-2 RAG Test System")
    print("=" * 50)
    
    # Sett API-nøkkel
    api_key = input("Skriv inn din Mistral API-nøkkel (eller trykk Enter hvis allerede satt): ").strip()
    if api_key:
        os.environ["MISTRAL_API_KEY"] = api_key
    
    print("\n📝 Skriv inn ditt konsultasjonsnotat:")
    print("(Trykk Enter to ganger for å avslutte)")
    print("-" * 50)
    
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    note_text = "\n".join(lines[:-1])  # Fjern siste tomme linje
    
    if not note_text.strip():
        print("❌ Ingen tekst funnet. Avslutter.")
        return
    
    print(f"\n🔍 Analyserer notatet...")
    print(f"Lengde: {len(note_text)} tegn")
    print("-" * 50)
    
    try:
        # Bruk streaming med visuell output
        result = infer(note_text, stream=True, show_stream=True)
        
        print("\n✅ Resultat:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Vis en sammendrag
        print("\n📊 Sammendrag:")
        for i, item in enumerate(result.get("top_k", []), 1):
            print(f"{i}. {item['code']} - {item['title']} (sikkerhet: {item['confidence']:.1%})")
            if item.get("needs_review"):
                print(f"   ⚠️  Krever gjennomgang")
        
        if result.get("notes"):
            print(f"\n💬 Kommentar: {result['notes']}")
            
    except Exception as e:
        print(f"❌ Feil: {e}")
        print("Sjekk at:")
        print("- API-nøkkelen er riktig")
        print("- Indeksen er bygget (kjør 'python build_index.py')")
        print("- Internettforbindelsen fungerer")

if __name__ == "__main__":
    main()
