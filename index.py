import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

if "client" not in st.session_state:
   st.session_state.client = OpenAI(
        api_key=st.secrets["OPENAI_API_KEY"]
   )

if "generating_state" not in st.session_state:
     st.session_state.generating_state = False

def get_prompt():
        leads_list = [st.session_state[f"lead_{i}"] for i in range(1,st.session_state.lead_count+1)]
        leads = ", ".join(leads_list)
        prompt = f"""
            Een korte beschrijving van het verhaal: {st.session_state.description}\n
            Het aantal hoofdrolspelers: {st.session_state.lead_count}\n
            De namen van de hoofdrolspelers: {
                leads
            }
        """
        return(prompt)

def get_story(prompt: str, system_prompt: str):
        completion = st.session_state.client.chat.completions.create(model="gpt-4-1106-preview", # instruct should have faster generation times
                                                  temperature=1.,
                                                  stream=False,
                                                  messages=[{"role": "system", "content": system_prompt},
                                                            {"role": "user", "content": prompt}])
        return (completion.choices[0].message.content)
    
def get_image(story:str):
    # Dali-2 is limited to 1000 chars as prompt. use first 1000 to generate the image
    story=story[:1000]
    response = st.session_state.client.images.generate(
    model="dall-e-3",
    prompt=story,
    size="1024x1024",
    quality="standard",
    n=1,
    )

    image_url = response.data[0].url
    return image_url

def clear_inputs():
     st.session_state.description = ""
     st.session_state.lead_count = 1
     st.session_state.lead_1 = ""
     for i in range(1, 0):
          st.session_state[f"lead_{i}"] = ""

def generate():
    try:

        results = st.empty()

        with results.container():
            print("Starting generation chain...")

            # Get user prompt from elements
            prompt = get_prompt()

            # Get full story
            print("Generating story...")
            system_prompt = "Je bent een schrijver van kinderverhaaltjes, je krijgt een korte beschrijving van een verhaal en enkele hoofdrolspelers. Schrijf hier een kort kinderverhaal over in kindvriendelijke taal. Vermijd onderwerpen zoals seks, drugs, geweld en criminaliteit. Belangrijk: maak het verhaal niet te lang. Mik op ongeveer een 1500 characters (spaties en leestekens inbegrepen.)"
            story = ""
            with st.spinner("Verhaal genereren..."):
                story = get_story(prompt, system_prompt)

            # Get concise story
            print("Summarizing story...")
            system_prompt = "Beschrijf dit kinderverhaal in kernwoorden, bekijk het als een hele beknopte samenvatting die als input gebruikt wordt als prompt voor DALL-E 3. Heel belangrijk: NIET LANGER DAN 1000 CHARACTERS."
            concise_story = ""
            with st.spinner("Verhaal samenvatten..."):
                concise_story = get_story(story, system_prompt)
                print(f'Concise story: {concise_story}')

            # Get image
            print("Generating image...")
            image_url = ""
            with st.spinner("Foto genereren..."):
                image_url = get_image(concise_story)
                print(f'Image url: {image_url}')

            st.success("Klaar met genereren!")
            st.image(image_url)
            st.write(story)

            print('-----')

            st.button("Clear", on_click=results.empty)

    # Catch any exception to show to person resposible on the floor
    except Exception as error:
         st.error(error)

    finally:
         clear_inputs()


# Center image using columns
image_url = "https://www.uhasselt.be/media/kzfjh2ll/50-jaar-uhasselt.png"
_, center_column, _ = st.columns(3)
center_column.markdown(f"""
        <img src='{image_url}' style='
            width: 175px;
            height: auto;
            display: block;
            text-align: center;
            margin-left: auto;
            margin-right: auto;
            padding-bottom: 20px;
        '/>
    """, unsafe_allow_html=True
)

story_description = st.text_area("Geef een korte beschrijving van je verhaal", placeholder="Een groep avonturiers die samen een draak verslaan", key="description")
lead_count = st.slider("Hoeveel hoofdrolspelers zijn er?", min_value=1, max_value=8, key="lead_count")

lead_upper_col = st.columns(4)
lead_lower_col = st.columns(4)

def add_inputs(n):        
    for i in range(1, n+1):
        if i <= 4:
            with lead_upper_col[i-1]:
                st.text_input(f"Naam hoofdrolspeler #{i}", key=f"lead_{i}")
        else:
            with lead_lower_col[i-5]:
                st.text_input(f"Naam hoofdrolspeler #{i}", key=f"lead_{i}")

add_inputs(lead_count)
st.button("Schrijf mijn verhaal!", on_click=generate)


    