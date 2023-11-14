from flask import Flask, render_template
import speech_recognition as sr
from gtts import gTTS
import os
import openai
import pygame

app = Flask(__name__)

pygame.mixer.init()

# Configuração da API da OpenAI
openai.api_key = "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"

def verifica_pyaudio():
    try:
        import pyaudio
        return True
    except ImportError:
        return False

def processar_comando_voz():
    if not verifica_pyaudio():
        return "Erro: PyAudio não encontrado. Verifique a instalação."

    r = sr.Recognizer()

    with sr.Microphone() as source:
        try:
            print("Ajustando para ruído ambiente. Aguarde...")
            r.adjust_for_ambient_noise(source, duration=5)
            print("Diga algo...")

            # Inicie a escuta, continue até 5 segundos ou até que não haja fala
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            return "Tempo esgotado. Processando resposta."

    try:
        print("Processando áudio...")
        comando = r.recognize_google(audio, language='pt-BR')
        print(f"Comando recebido: {comando}")
        return comando.lower()
    except sr.UnknownValueError:
        print("Não foi possível entender o comando.")
        return ""

def reproduzir_resposta(resposta):
    # Utilizar gTTS para converter a resposta em áudio
    tts = gTTS(text=resposta, lang='pt')
    tts.save("static/resposta.mp3")

    # Reproduzir o arquivo de áudio com Pygame
    pygame.mixer.music.load("static/resposta.mp3")
    pygame.mixer.music.play()

@app.route('/')
def home():
    if not verifica_pyaudio():
        return "Erro: PyAudio não encontrado. Verifique a instalação."
    return render_template('index.html')

@app.route('/ouvir_comando', methods=['GET', 'POST'])
def ouvir_comando():
    comando = processar_comando_voz()

    if "erro" in comando.lower():
        return render_template('index.html', resposta=comando)

    if comando in ["shati", "shate", "xete", "chati"]:
        resposta = "Olá! Como posso ajudar?"
    else:
        resposta = "Desculpe, não entendi o comando."

    # Utilizar OpenAI para gerar uma resposta mais elaborada
    resposta_openai = openai.Completion.create(
        engine="davinci-002",
        prompt=resposta,
        temperature=1.7,
        max_tokens=300
    )

    resposta_final = resposta_openai["choices"][0]["text"].strip()

    # Reproduzir a resposta com Pygame
    reproduzir_resposta(resposta_final)

    return render_template('index.html', resposta=resposta_final)

if __name__ == '__main__':
    app.run(debug=True)
