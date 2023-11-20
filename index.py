import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

if "client" not in st.session_state:
   st.session_state.client = OpenAI()


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
        completion = st.session_state.client.chat.completions.create(model="gpt-3.5-turbo",
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

def generate():
    print("Starting generation chain...")

    # Get user prompt from elements
    prompt = get_prompt()
    st.write(prompt)

    ## Get full story
    print("Generating story...")
    system_prompt = "Jij bent een schrijver van kinderverhaaltjes. Je krijgt een korte beschrijving van een verhaal, het aantal hoofdrolspelers en hun namen. Schrijf hier een verhaal over in kindvriendelijke taal en taal die de content-policy van Dall-E respecteert door thema's zoals geweld, sex, drugs en criminaliteit te vermijden."
    story = get_story(prompt, system_prompt)
    st.write(story)

    # Get concise story
    print("Summarizing story...")
    system_prompt = "Vat dit kinderverhaal samen naar zijn essentie, het moet de vorm hebben van een prompt voor Dall-E 2/3. Gebruik kindvriendelijke taal. Probeer het samen te vatten in ongeveer 900 characters (inclusief spaties en leestekens). Heel belangrijk: NIET LANGER DAN 1000 CHARACTERS."
    concise_story = get_story(story, system_prompt)
    st.write(concise_story)
    
    # Get image
    print("Generating image...")
    image_url = get_image(concise_story)
    st.image(image_url)

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


    