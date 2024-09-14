import streamlit as st
import requests

# Set page configuration
st.set_page_config(
    page_title="Image Upload and Form Submission",
    page_icon="♥️",
    layout="centered",
    initial_sidebar_state="auto",
)

# Initialize error state
if 'errors' not in st.session_state:
    st.session_state['errors'] = {}

# Title of the app
st.title(":spades::clubs:ExplainableGTO:hearts::diamonds:")

# Provide explanations for each option
st.markdown("""
**Select Analytics Type:**

- **Game**: Upload your game information directly, and the system will help analyze it.
- **GTO**: Upload a screenshot of GTO analysis from your choice of game scenario, and the system will help analyze it.
""")

# Type selection radio button (Game or GTO)
image_type = st.radio("", ('Game', 'GTO'))

if image_type == 'Game':
    st.subheader("Game Information")

    # Display example data in an expandable section
    with st.expander("Click here to see an example of how to fill each field"):
        st.json({
            "effective_stack": 100,
            "hole_cards": "As,Td",
            "pot_preflop": 50,
            "preflop_action": "UTG,CO,UTG",
            "flop_cards": "Kh,7s,2d",
            "flop_bet": 25,
            "turn_card": "5c",
            "turn_bet": 50,
            "river_card": "Qd",
            "river_bet": 75
        })

    # Image uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key='game_image_uploader')

    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
    else:
        # Clear the session_state fields if no image is uploaded
        st.session_state['effective_stack'] = ''
        st.session_state['hole_cards'] = ''
        st.session_state['pot_before_flop'] = ''
        st.session_state['preflop_action'] = ''
        st.session_state['flop_cards'] = ''
        st.session_state['flop_bet'] = ''
        st.session_state['turn_card'] = ''
        st.session_state['turn_bet'] = ''
        st.session_state['river_card'] = ''
        st.session_state['river_bet'] = ''

    # Auto-fill button
    if st.button('Auto-fill from Image'):
        if uploaded_file is not None:
            with st.spinner('Extracting information from the image...'):
                # Send image to backend to extract info
                files = {'image': uploaded_file.getvalue()}
                response = requests.post('http://127.0.0.1:5000/fill', files={'image': uploaded_file})
                if response.status_code == 200:
                    extracted_info = response.json()
                    # Update st.session_state with extracted info
                    st.session_state['effective_stack'] = extracted_info.get('effective_stack', '')
                    st.session_state['hole_cards'] = extracted_info.get('hole_cards', '')
                    st.session_state['pot_before_flop'] = extracted_info.get('pot_before_flop', '')
                    st.session_state['preflop_action'] = extracted_info.get('preflop_action', '')
                    st.session_state['flop_cards'] = extracted_info.get('flop_cards', '')
                    st.session_state['flop_bet'] = extracted_info.get('flop_bet', '')
                    st.session_state['turn_card'] = extracted_info.get('turn_card', '')
                    st.session_state['turn_bet'] = extracted_info.get('turn_bet', '')
                    st.session_state['river_card'] = extracted_info.get('river_card', '')
                    st.session_state['river_bet'] = extracted_info.get('river_bet', '')
                    st.success('Form auto-filled from the image!')
                else:
                    st.error('Error extracting information from the image.')
        else:
            st.warning('Please upload an image before using auto-fill.')

    with st.form(key='game_form', clear_on_submit=False):
        # Inform the user about Enter key behavior
        st.info("**Note:** Pressing Enter will submit the form. Please use Tab or click to navigate between fields.")

        # The form fields with help text and error messages
        effective_stack = st.text_input(
            "Effective stack",
            value=st.session_state.get('effective_stack', ''),
            key='effective_stack',
            help="Enter the smallest stack size at the beginning of the hand (e.g., 100)"
        )
        if st.session_state['errors'].get('Effective stack'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        hole_cards = st.text_input(
            "Hole Cards",
            value=st.session_state.get('hole_cards', ''),
            key='hole_cards',
            help="Enter your hole cards separated by a comma (e.g., 'As,Td')"
        )
        if st.session_state['errors'].get('Hole Cards'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        pot_before_flop = st.text_input(
            "Pot before flop",
            value=st.session_state.get('pot_before_flop', ''),
            key='pot_before_flop',
            help="Enter the total pot size before the flop (e.g., 50)"
        )
        if st.session_state['errors'].get('Pot before flop'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        preflop_action = st.text_input(
            "Preflop action",
            value=st.session_state.get('preflop_action', ''),
            key='preflop_action',
            help="Describe the preflop actions (e.g., 'UTG raises to 5, CO calls, UTG calls')"
        )
        if st.session_state['errors'].get('Preflop action'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        flop_cards = st.text_input(
            "Flop Cards",
            value=st.session_state.get('flop_cards', ''),
            key='flop_cards',
            help="Enter the flop cards separated by commas (e.g., 'Kh,7s,2d')"
        )
        if st.session_state['errors'].get('Flop Cards'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        flop_bet = st.text_input(
            "Flop bet",
            value=st.session_state.get('flop_bet', ''),
            key='flop_bet',
            help="Enter the bet amount on the flop (e.g., 25)"
        )
        if st.session_state['errors'].get('Flop bet'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        turn_card = st.text_input(
            "Turn card",
            value=st.session_state.get('turn_card', ''),
            key='turn_card',
            help="Enter the turn card (e.g., '5c')"
        )
        if st.session_state['errors'].get('Turn card'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        turn_bet = st.text_input(
            "Turn bet",
            value=st.session_state.get('turn_bet', ''),
            key='turn_bet',
            help="Enter the bet amount on the turn (e.g., 50)"
        )
        if st.session_state['errors'].get('Turn bet'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        river_card = st.text_input(
            "River card",
            value=st.session_state.get('river_card', ''),
            key='river_card',
            help="Enter the river card (e.g., 'Qd')"
        )
        if st.session_state['errors'].get('River card'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)

        river_bet = st.text_input(
            "River bet",
            value=st.session_state.get('river_bet', ''),
            key='river_bet',
            help="Enter the bet amount on the river (e.g., 75)"
        )
        if st.session_state['errors'].get('River bet'):
            st.markdown(f"<span style='color:red; font-size: small;'>This field is required.</span>", unsafe_allow_html=True)
            
        submit_button = st.form_submit_button(label='Submit for Game Analysis')

    if submit_button:
        # Collect field values
        effective_stack = st.session_state.get('effective_stack', '')
        hole_cards = st.session_state.get('hole_cards', '')
        pot_before_flop = st.session_state.get('pot_before_flop', '')
        preflop_action = st.session_state.get('preflop_action', '')
        flop_cards = st.session_state.get('flop_cards', '')
        flop_bet = st.session_state.get('flop_bet', '')
        turn_card = st.session_state.get('turn_card', '')
        turn_bet = st.session_state.get('turn_bet', '')
        river_card = st.session_state.get('river_card', '')
        river_bet = st.session_state.get('river_bet', '')

        # Check if any required form field is empty
        required_fields = {
            'Effective stack': effective_stack,
            'Hole Cards': hole_cards,
            'Pot before flop': pot_before_flop,
            'Preflop action': preflop_action,
            'Flop Cards': flop_cards,
            'Flop bet': flop_bet,
            'Turn card': turn_card,
            'Turn bet': turn_bet,
            'River card': river_card,
            'River bet': river_bet,
        }

        empty_fields = [field_name for field_name, value in required_fields.items() if not value]

        if empty_fields:
            st.warning(f"Please fill out all required fields before submitting.")
            # Update the error state
            st.session_state['errors'] = {field_name: True for field_name in empty_fields}
        else:
            # Clear any previous errors
            st.session_state['errors'] = {}
            # Prepare data to send
            data = {
                'effective_stack': effective_stack,
                'hole_cards': hole_cards,
                'pot_before_flop': pot_before_flop,
                'preflop_action': preflop_action,
                'flop_cards': flop_cards,
                'flop_bet': flop_bet,
                'turn_card': turn_card,
                'turn_bet': turn_bet,
                'river_card': river_card,
                'river_bet': river_bet,
                'is_game': True
            }
            with st.spinner('Submitting data for analysis...'):
                # Send image and data to backend
                response = requests.post('http://127.0.0.1:5000/upload', files={'image': uploaded_file}, data=data)
                if response.status_code == 200:
                    st.success('Your data has been submitted successfully!')
                else:
                    st.error('Error submitting the data. Please try again.')
        


elif image_type == 'GTO':
    st.subheader("Upload Image for GTO Analysis")

    # Provide explanation
    st.info("**GTO Analysis**: Upload a screenshot of GTO analysis from your choice of game scenario, and the system will help analyze it.")

    with st.form(key='gto_form'):
        # Image uploader
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key='gto_image_uploader')

        # Display uploaded image
        if uploaded_file is not None:
            st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

        # Submit button
        submit_button = st.form_submit_button(label='Submit for GTO Analysis')

    if submit_button:
        if uploaded_file is not None:
            with st.spinner('Submitting image for GTO analysis...'):
                # Prepare data
                data = {'is_game': False}
                # Send image to backend
                response = requests.post('http://127.0.0.1:5000/upload', files={'image': uploaded_file}, data=data)
                if response.status_code == 200:
                    st.success('Your image has been submitted successfully!')
                else:
                    st.error('Error submitting the image. Please try again.')
        else:
            st.warning('Please upload an image before submitting.')
