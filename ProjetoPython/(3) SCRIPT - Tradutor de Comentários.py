# -*- coding: utf-8 -*-

# Introdução à Programação com Python
# MBA em Data Science, Inteligência Artificial e Analytics USP/ESALQ

#%% Instalando o pacote necessário

# Executar a seguinte instalação no console (sem o #) 

# pip install deep-translator

#%% Importando os pacotes

import io
import time
import tokenize
from deep_translator import GoogleTranslator

#%% Indicar o texto que deverá ser traduzido

# Nota: manter as aspas (""") no início e fim (o texto deve ficar entre elas)

code = """

#%% Numérico

# Na função a seguir, note que é comum atribuir apelidos aos pacotes "pd"
# A partir de agora, sempre que usarmos o pandas será com o nome "pd"
# Na sequência, indicamos a função "Series" que está no pacote "pd"

numeros = pd.Series([10, 20, 30, 40, 50, 60, 70, 80])

print(numeros)

"""
#%% Definindo a função (pode alterar o idioma destino "target" na linha 38)

translator = GoogleTranslator(source='pt', target='en')

def translate_comment(comment, translator, retries=5, delay=2):

    for attempt in range(retries):
        try:
            return translator.translate(comment)
        except Exception as e:
            print(f"Erro ao traduzir: {e}. Tentativa {attempt + 1} de {retries}.")
            time.sleep(delay)
    return comment

def translate_comments(code, translator):

    comments = {}
    reader = io.StringIO(code).readline
    tokens = list(tokenize.generate_tokens(reader))

    for toknum, tokval, start, end, line in tokens:
        if toknum == tokenize.COMMENT:
            line_no = start[0]
            original = tokval
            after_hash = original[1:]
            spaces_after = len(after_hash) - len(after_hash.lstrip(' '))
            comment_text = after_hash.lstrip(' ')

            if comment_text.strip():
                translated = translate_comment(comment_text, translator)
                new_comment = f"#{' ' * spaces_after}{translated}"
                comments[line_no] = new_comment

    new_lines = []
    for i, line in enumerate(code.splitlines(), start=1):
        if i in comments:
            hash_index = line.index('#')
            before = line[:hash_index]
            new_lines.append(before + comments[i])
        else:
            new_lines.append(line)

    return "\n".join(new_lines)

#%% Gerando a tradução

translated_code = translate_comments(code, translator)
print(translated_code)

#%% Fim!