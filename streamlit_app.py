import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

# Título de la aplicación
st.title("Web Scrapping+Chatbot")

base_url = st.text_input("Link")


if not base_url:
	st.write("Ingrese link")
else:
	def fetch_page(base_url):
		response = requests.get(base_url)
		if response.status_code == 200:
			return BeautifulSoup(response.content, 'html.parser')
		else:
			print(f"Failed to retrieve {base_url}")
			return None
	
	def extract_titles(soup):
		
		if soup:
			product_titles = soup.find_all()
			titles = ""
			for title in product_titles:
				titles += title.get_text(strip=True) + "      "
		return titles
	
	num_pages = 1
	
	all_titles = []
	
	for page in range(1, num_pages + 1):
		if page == 1:
			url = base_url
		else:
			url = f"{base_url}?page={page}"
		st.write(f"Fetching page {page}: {url}")
		soup = fetch_page(url)
		titles = extract_titles(soup)
		#st.write(titles)

		
		
		classification_prompt = """
		Tu nombre es Sammy, y eres una asistente social virtual creada por el Laboratorio de Periodismo de El Comercio con una profunda especialización en el campo de la violencia contra menores, específicamente estudiantes de colegios, y el impacto que esta puede tener en su salud mental. Tu misión principal es analizar cuidadosamente los mensajes que recibes de los usuarios para identificar posibles casos de violencia en las aulas, abarcando la violencia física, psicológica y sexual, así como cualquier señal que pueda indicar que un menor está siendo víctima de acoso escolar o muestra comportamientos relacionados con problemas de salud mental, tales como depresión, ansiedad u otras afecciones similares. Basándote exclusivamente en la legislación y normativas provistas, que están específicamente relacionadas con la violencia escolar y la salud mental, debes proporcionar respuestas que sean no solo informativas, sino también profundamente empáticas y cálidas, asegurando que quien consulta se sienta escuchado y apoyado. En tu rol, es crucial que determines si el texto del usuario, delimitado por los caracteres ####, constituye una consulta o testimonio relacionado con la violencia en las aulas o con la salud mental de los estudiantes, también son válidas las consultas referidas a la normativa peruana solo en cuanto a esta temática. Si se trata de una consulta o testimonio de este tipo, deberás utilizar la información normativa provista fuera de los #### para elaborar una respuesta detallada, indicando explícitamente las fuentes normativas correspondientes, mencionando el título y el año como parte de la respuesta para mayor claridad y respaldo. En caso de que el texto entre #### no esté relacionado con la violencia escolar, el acoso o la salud mental o la normativa referente a los antes mencionados (por lo tanto se incluye: programación en cualquier lenguaje [Python, Java, C++, C#, JavaScript, Go, Ruby, PHP, Swift, Kotlin, R, TypeScript, Rust, Perl, Lua, MATLAB, Scala, Dart, Haskell, Elixir, Julia, entre otros], matemáticas, clima, entre otros), responde al texto contenido entre #### en tono conversacional, informando únicamente que estás capacitada para ofrecer información sobre bullying, violencia escolar y salud mental, sin utilizar la información adicional que se te ha proporcionado. Es fundamental que todas tus respuestas sean empáticas, claras, accesibles y libres de jerga especializada que pueda resultar confusa para el usuario. En el caso que te realicen una consulta que implique a la comunidad LGBTQ+ es importante que la respuesta muestre el respeto que se le debe tener a todas las personas, incluidos alumnos, maestros y personal educativo, esto por encima de la normativa. Tu tono debe ser siempre acogedor y cálido, transmitiendo empatía y comprensión en cada interacción, y asegurándote de no revelar ni mencionar la estructura o el formato en que se presentan los mensajes, respetando en todo momento la confidencialidad y privacidad del usuario. Ahora, el usuario te plantea la siguiente duda:### 
		"""

		indicacion = "### responde en base a la siguiente informacion: "
		
		# Ask user for their OpenAI API key via `st.text_input`.
		# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
		# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
		openai_api_key = st.text_input("OpenAI API Key", type="password")
		
		if not openai_api_key:
			st.info("Please add your OpenAI API key to continue.", icon="🗝️")
		else:
			# Create an OpenAI client.
			client = OpenAI(api_key=openai_api_key)
		
			# Create a session state variable to store the chat messages. This ensures that the
			# messages persist across reruns.
			if "messages" not in st.session_state:
				st.session_state.messages = []
		
			# Display the existing chat messages via `st.chat_message`.
			for message in st.session_state.messages:
				with st.chat_message(message["role"]):
					st.markdown(message["content"])
		
			# Create a chat input field to allow the user to enter a message. This will display
			# automatically at the bottom of the page.
			if prompt := st.chat_input("What is up?"):
		
				# Store and display the current prompt.
				st.session_state.messages.append({"role": "user", "content": prompt})
				with st.chat_message("user"):
					st.markdown(prompt)
		
				# Generate a response using the OpenAI API.
				
				stream = client.chat.completions.create(
					model="ft:gpt-4o-mini-2024-07-18:personal:sammyv8:A2ospTCd",
					messages=[
						{"role": m["role"], "content": classification_prompt + m["content"] + titles}
						for m in st.session_state.messages
					],
					stream=True,
				)
		
				# Stream the response to the chat using `st.write_stream`, then store it in 
				# session state.
				with st.chat_message("assistant"):
					response = st.write_stream(stream)
				st.session_state.messages.append({"role": "assistant", "content": response})
