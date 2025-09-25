import streamlit as st
import pyttsx3
import threading
from db import get_user_id, save_symptom_check

def speak_text(text):
    def _speak():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    thread = threading.Thread(target=_speak)
    thread.start()

def render_symptom_checker(predictor, df, symptoms, symptom_descriptions):
    # Allow symptom checker usage without login
    # if not st.session_state.logged_in:
    #     st.error("Please log in to use the Symptom Checker.")
    #     if st.button("Go to Login"):
    #         st.session_state.page = "login"
    #         st.rerun()
    #     return

    # Create columns to center content horizontally
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Step 1: Age and Sex input
        if st.session_state.step == 1:
            st.title("Symptom Checker")
            st.write("Identify possible conditions and treatment related to your symptoms.")
            st.write("This tool does not provide medical advice.")
            st.write("")

            age = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.age if st.session_state.age else 30)
            sex = st.radio("Sex", options=["Male", "Female"], index=0 if st.session_state.sex == "Male" else 1 if st.session_state.sex == "Female" else 0, horizontal=True)

            if st.button("Continue"):
                st.session_state.age = age
                st.session_state.sex = sex
                st.session_state.step = 2
                st.rerun()

        # Step 2: Symptom selection
        elif st.session_state.step == 2:
            st.title("Select Your Symptoms")
            st.write("Check the boxes for symptoms you're experiencing:")

            selected_symptoms = {}
            for symptom in symptoms:
                description = symptom_descriptions.get(symptom, symptom.replace('_', ' ').title())
                selected = st.checkbox(
                    f"{symptom.replace('_', ' ').title()}",
                    help=description,
                    value=st.session_state.selected_symptoms.get(symptom, False),
                    key=symptom
                )
                selected_symptoms[symptom] = selected

            if st.button("Back"):
                st.session_state.step = 1
                st.rerun()

            if st.button("Get Prediction"):
                if not any(selected_symptoms.values()):
                    st.warning("Please select at least one symptom to continue.")
                else:
                    st.session_state.selected_symptoms = selected_symptoms
                    st.session_state.step = 3
                    st.rerun()

        # Step 3: Prediction results (Conditions)
        elif st.session_state.step == 3:
            st.title("Possible Conditions")
            st.write(f"Age: {st.session_state.age} | Sex: {st.session_state.sex}")
            st.write("Based on your symptoms, here are the possible conditions:")

            # Prepare input for prediction
            symptom_input = {symptom: int(selected) for symptom, selected in st.session_state.selected_symptoms.items()}

            try:
                result = predictor.predict_disease(symptom_input, df)
                st.session_state.prediction_result = result
            except Exception as e:
                st.error(f"Error making prediction: {e}")
                return

            if st.session_state.prediction_result:
                primary = st.session_state.prediction_result['primary_prediction']
                confidence = st.session_state.prediction_result['primary_probability']
                st.subheader(f"Most Likely Condition: {primary}")
                st.write(f"Confidence: {confidence:.1%}")

                if st.button("Speak Result"):
                    speak_text(f"Most Likely Condition: {primary} with confidence {confidence:.1%}")

                st.markdown("---")
                st.subheader("Other Possible Conditions")
                for pred in st.session_state.prediction_result['all_predictions'][1:4]:
                    st.write(f"- {pred['disease']} ({pred['probability']:.1%} confidence)")

                # Save symptom check if logged in
                if st.session_state.logged_in:
                    user_id = get_user_id(st.session_state.username)
                    if user_id:
                        save_symptom_check(
                            user_id=user_id,
                            age=st.session_state.age,
                            sex=st.session_state.sex,
                            symptoms=st.session_state.selected_symptoms,
                            prediction=st.session_state.prediction_result
                        )

            if st.button("Back"):
                st.session_state.step = 2
                st.rerun()

            if st.button("Next"):
                st.session_state.step = 4
                st.rerun()

        # Step 4: Details placeholder
        elif st.session_state.step == 4:
            st.title("Details")
            st.write("More information about the conditions and symptoms will be shown here.")
            if st.button("Back"):
                st.session_state.step = 3
                st.rerun()
            if st.button("Next"):
                st.session_state.step = 5
                st.rerun()

        # Step 5: Treatment placeholder
        elif st.session_state.step == 5:
            st.title("Treatment")
            st.write("Treatment options and recommendations will be shown here.")
            if st.button("Back"):
                st.session_state.step = 4
                st.rerun()
            if st.button("Restart"):
                st.session_state.step = 1
                st.session_state.age = None
                st.session_state.sex = None
                st.session_state.selected_symptoms = {}
                st.session_state.prediction_result = None
                st.rerun()
