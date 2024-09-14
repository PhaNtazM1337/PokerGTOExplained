import streamlit as st
import requests
import json


def dict_to_markdown(d, level=0):
    md_content = ""
    indent = "  " * level
    for key, value in d.items():
        if isinstance(value, dict):
            md_content += f"{indent}- **{key}**:\n"
            md_content += dict_to_markdown(value, level + 1)
        elif isinstance(value, list):
            md_content += f"{indent}- **{key}**:\n"
            for item in value:
                md_content += f"{indent}  - {item}\n"
        else:
            md_content += f"{indent}- **{key}**:\n {value}\n"
    return md_content


# def dict_to_html(d, level=0):
#     html_content = ""
#     indent = "  " * level
#     for key, value in d.items():
#         if isinstance(value, dict):
#             html_content += f"{indent}<h3 style='color:blue;'>{key}</h3>\n"
#             html_content += dict_to_html(value, level + 1)
#         else:
#             html_content += f"{indent}<h3 style='color:blue;'>{key}</h3>\n"
#             html_content += f"{indent}<p>{value}</p>\n"
#     return html_content


def dict_to_html(d, level=0):
    html_content = ""
    indent = "  " * level * 2  # Increase indentation for nested levels
    header_size = min(
        level + 3, 6
    )  # Decrease header size as depth increases (from h3 to h6)
    margin = f"margin-left: {level * 30}px;"
    for key, value in d.items():
        if isinstance(value, dict):
            html_content += f"<h{header_size} style='color:#EE82EE; {margin}'>{indent}{key}</h{header_size}>\n"
            html_content += dict_to_html(value, level + 1)
        else:
            html_content += f"<h{header_size} style='color:#EE82EE; {margin}'>{indent}{key}</h{header_size}>\n"
            html_content += f"<p style = '{margin}'>{indent}{value}<br><br></p>"
    return html_content


# Set page configuration
st.set_page_config(
    page_title="Image Upload and Form Submission",
    page_icon="♥️",
    layout="centered",
    initial_sidebar_state="auto",
)

# Initialize session state variables
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None

if "errors" not in st.session_state:
    st.session_state["errors"] = {}

# Initialize form fields in session state
form_fields = [
    "effective_stack",
    "hole_cards",
    "pot_before_flop",
    "preflop_action",
    "flop_cards",
    "flop_action",
    "turn_card",
    "turn_action",
    "river_card",
    "river_action",
    "final_pot",
]

for field in form_fields:
    if field not in st.session_state:
        st.session_state[field] = ""

# Title of the app
st.title(":spades::clubs:ExplainableGTO:hearts::diamonds:")

# Provide explanations for each option
st.markdown(
    """
**Select Analytics Type:**

- **Game**: Upload your game information directly, and the system will help analyze it.
- **GTO**: Upload a screenshot of GTO analysis from your choice of game scenario, and the system will help analyze it.
"""
)

# Type selection radio button (Game or GTO)
image_type = st.radio("", ("Game", "GTO"))

if image_type == "Game":
    st.subheader("Game Information")

    # Display example data in an expandable section
    with st.expander("Click here to see an example of how to fill each field"):
        st.json(
            {
                "effective_stack": 100,
                "hole_cards": "As,Td",
                "pot_preflop": 50,
                "preflop_action": "UTG,CO,UTG",
                "flop_cards": "Kh,7s,2d",
                "flop_action": "c,15,45,c ## call and check are both c",
                "turn_card": "5c",
                "turn_action": 50,
                "river_card": "Qd",
                "river_action": 75,
                "final_pot": 100,
            }
        )

    # Image uploader
    uploaded_file = st.file_uploader(
        "Choose an image...", type=["jpg", "jpeg", "png"], key="game_image_uploader"
    )

    # Manage uploaded_file in session state
    if uploaded_file is not None:
        st.session_state["uploaded_file"] = uploaded_file
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    else:
        uploaded_file = st.session_state.get("uploaded_file", None)
        if uploaded_file is not None:
            # Display uploaded image from session state
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Auto-fill button
    if st.button("Auto-fill from Image"):
        if uploaded_file is not None:
            with st.spinner("Extracting information from the image..."):
                # Send image to backend to extract info
                files = {"image": uploaded_file.getvalue()}
                response = requests.post(
                    "http://127.0.0.1:5000/fill", files={"image": uploaded_file}
                )
                if response.status_code == 200:
                    extracted_info = response.json()
                    # Update st.session_state with extracted info
                    st.session_state["effective_stack"] = extracted_info.get(
                        "effective_stack", ""
                    )
                    st.session_state["hole_cards"] = extracted_info.get(
                        "hole_cards", ""
                    )
                    st.session_state["pot_before_flop"] = extracted_info.get(
                        "pot_before_flop", ""
                    )
                    st.session_state["preflop_action"] = extracted_info.get(
                        "preflop_action", ""
                    )
                    st.session_state["flop_cards"] = extracted_info.get(
                        "flop_cards", ""
                    )
                    st.session_state["flop_action"] = extracted_info.get(
                        "flop_action", ""
                    )
                    st.session_state["turn_card"] = extracted_info.get("turn_card", "")
                    st.session_state["turn_action"] = extracted_info.get(
                        "turn_action", ""
                    )
                    st.session_state["river_card"] = extracted_info.get(
                        "river_card", ""
                    )
                    st.session_state["river_action"] = extracted_info.get(
                        "river_action", ""
                    )
                    st.session_state["final_pot"] = extracted_info.get("final_pot", "")
                    st.success("Form auto-filled from the image!")
                else:
                    st.error("Error extracting information from the image.")
        else:
            st.warning("Please upload an image before using auto-fill.")

    with st.form(key="game_form", clear_on_submit=False):
        # Inform the user about Enter key behavior
        st.info(
            "**Note:** Pressing Enter will submit the form. Please use Tab or click to navigate between fields."
        )

        # The form fields with help text and error messages
        effective_stack = st.text_input(
            "Effective stack",
            value=st.session_state.get("effective_stack", None),
            key="effective_stack",
            help="Enter the smallest stack size at the beginning of the hand (e.g., 100)",
        )

        hole_cards = st.text_input(
            "Hole Cards",
            value=st.session_state.get("hole_cards", None),
            key="hole_cards",
            help="Enter your hole cards separated by a comma (e.g., 'As,Td')",
        )

        pot_before_flop = st.text_input(
            "Pot before flop",
            value=st.session_state.get("pot_before_flop", None),
            key="pot_before_flop",
            help="Enter the total pot size before the flop (e.g., 50)",
        )

        preflop_action = st.text_input(
            "Preflop action",
            value=st.session_state.get("preflop_action", None),
            key="preflop_action",
            help="Describe the preflop actions (e.g., 'UTG raises to 5, CO calls, UTG calls')",
        )

        flop_cards = st.text_input(
            "Flop Cards",
            value=st.session_state.get("flop_cards", None),
            key="flop_cards",
            help="Enter the flop cards separated by commas (e.g., 'Kh,7s,2d')",
        )

        flop_action = st.text_input(
            "Flop action",
            value=st.session_state.get("flop_action", None),
            key="flop_action",
            help="Enter the flop action on the flop (e.g. c,15,45,c)",
        )

        turn_card = st.text_input(
            "Turn card",
            value=st.session_state.get("turn_card", None),
            key="turn_card",
            help="Enter the turn card (e.g., '5c')",
        )

        turn_action = st.text_input(
            "Turn action",
            value=st.session_state.get("turn_action", None),
            key="turn_action",
            help="Enter the bet amount on the turn (e.g., 50)",
        )

        river_card = st.text_input(
            "River card",
            value=st.session_state.get("river_card", None),
            key="river_card",
            help="Enter the river card (e.g., 'Qd')",
        )

        river_action = st.text_input(
            "River bet",
            value=st.session_state.get("river_action", None),
            key="river_action",
            help="Enter the bet amount on the river (e.g., 75)",
        )

        final_pot = st.text_input(
            "Final Pot",
            value=st.session_state.get("final_pot", None),
            key="final_pot",
            help="Enter the final pot so far (e.g., 100)",
        )

        submit_button = st.form_submit_button(label="Submit for Game Analysis")

    if submit_button:
        # Collect field values
        effective_stack = st.session_state.get("effective_stack", "")
        hole_cards = st.session_state.get("hole_cards", "")
        pot_before_flop = st.session_state.get("pot_before_flop", "")
        preflop_action = st.session_state.get("preflop_action", "")
        flop_cards = st.session_state.get("flop_cards", "")
        flop_action = st.session_state.get("flop_action", "")
        turn_card = st.session_state.get("turn_card", "")
        turn_action = st.session_state.get("turn_action", "")
        river_card = st.session_state.get("river_card", "")
        river_action = st.session_state.get("river_action", "")
        final_pot = st.session_state.get("final_pot", "")

        # Check if any required form field is empty
        required_fields = {
            "Effective stack": effective_stack,
            "Hole Cards": hole_cards,
            "Pot before flop": pot_before_flop,
            "Preflop action": preflop_action,
            "Flop Cards": flop_cards,
            "Flop action": flop_action,
            "Turn card": turn_card,
            "Turn action": turn_action,
            "River card": river_card,
            "River bet": river_action,
            "Final Pot": final_pot,
        }

        # Clear any previous errors
        st.session_state["errors"] = {}
        # Prepare data to send
        data = {
            "effective_stack": effective_stack,
            "hole_cards": hole_cards,
            "pot_before_flop": pot_before_flop,
            "preflop_action": preflop_action,
            "flop_card": flop_cards,
            "flop_action": flop_action,
            "turn_card": turn_card,
            "turn_action": turn_action,
            "river_card": river_card,
            "river_action": river_action,
            "final_pot": final_pot,
            "is_game": True,
        }
        with st.spinner("Submitting data for analysis..."):
            # Check if uploaded_file exists in session state
            uploaded_file = st.session_state.get("uploaded_file", None)
            if uploaded_file is not None:
                # Send image and data to backend
                response = requests.post(
                    "http://127.0.0.1:5000/upload",
                    files={"image": uploaded_file},
                    data=data,
                )
            else:
                # Send data without image
                print(data)
                response = requests.post("http://127.0.0.1:5000/submit", data=data)

            if response.status_code == 200:
                st.success("Your data has been submitted successfully!")
                gto_response = response.json()
                markdown_data = dict_to_markdown(gto_response)
                html_data = dict_to_html(gto_response)
                # display_json_hierarchy(gto_response)
                # st.markdown(markdown_data)
                st.markdown(html_data, unsafe_allow_html=True)
            else:
                st.error("Error submitting the data. Please try again.")

elif image_type == "GTO":
    st.subheader("Upload Image for GTO Analysis")

    # Provide explanation
    st.info(
        "**GTO Analysis**: Upload a screenshot of GTO analysis from your choice of game scenario, and the system will help analyze it."
    )

    with st.form(key="gto_form"):
        # Image uploader
        uploaded_file = st.file_uploader(
            "Choose an image...", type=["jpg", "jpeg", "png"], key="gto_image_uploader"
        )

        # Manage uploaded_file in session state
        if uploaded_file is not None:
            st.session_state["uploaded_file"] = uploaded_file
            # Display uploaded image
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        else:
            uploaded_file = st.session_state.get("uploaded_file", None)
            if uploaded_file is not None:
                # Display uploaded image from session state
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Submit button
        submit_button = st.form_submit_button(label="Submit for GTO Analysis")

    if submit_button:
        uploaded_file = st.session_state.get("uploaded_file", None)
        if uploaded_file is not None:
            with st.spinner("Submitting image for GTO analysis..."):
                # Prepare data
                data = {"is_game": False}
                # Send image to backend
                response = requests.post(
                    "http://127.0.0.1:5000/upload",
                    files={"image": uploaded_file},
                    data=data,
                )
                if response.status_code == 200:
                    st.success("Your image has been submitted successfully!")
                    gto_response = response.json()
                    markdown_data = dict_to_markdown(gto_response)
                    html_data = dict_to_html(gto_response)
                    # display_json_hierarchy(gto_response)
                    # st.markdown(markdown_data)
                    st.markdown(html_data, unsafe_allow_html=True)
                else:
                    st.error("Error submitting the image. Please try again.")
        else:
            st.warning("Please upload an image before submitting.")
