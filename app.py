from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Predefined set of questions
QUESTIONS = [
    {"id": "eye_contact", "text": "Child avoids eye contact"},
    {"id": "response_to_name", "text": "Does not respond when their name is called"},
    {"id": "uses_gestures", "text": "Uses gestures to communicate"},
    {"id": "play_behavior", "text": "Prefer to play alone"},
    {"id": "verbal_communication", "text": "Struggles to engage in verbal communication with others"},
    {"id": "social_smiling", "text": "Does not smile back when someone smiles at them"},
    {"id": "shared_interest", "text": "Uninterested in what others are doing"},
    {"id": "follows_direction", "text": "Struggles following sequential steps"},
    {"id": "repetitive_behaviors", "text": "Repetitive behaviors (rocking, spinning, hand-flapping)"},
    {"id": "routines_or_rituals", "text": "Insistent on sticking to certain routines or rituals"},
    {"id": "intense_interests", "text": "Has intense interests in specific subjects or activities"},
    {"id": "reacts_to_changes", "text": "Reacts to changes in their routine"},
    {"id": "handles_frustration", "text": "Unable to control frustration"},
    {"id": "shows_empathy", "text": "Lacks empathy towards others?"},
    {"id": "calming_strategies", "text": "Unable to calm themselves down"},
    {"id": "age_started_speaking", "text": "Delay or absence of typical developmental speech milestones"},
    {"id": "uses_language", "text": "Using language not typical for their age"},
    {"id": "imaginative_play", "text": "Engages in imaginative play?"},
    {"id": "unusual_speech_patterns", "text": "Uses repetitive or atypical speech patterns"},
    {"id": "unusual_reactions", "text": "Has unusual reactions to sensory experiences"},
    {"id": "clothing_textures_intolerance", "text": "Shows intolerance to certain clothing textures"},
    {"id": "seeks_sensory_experiences", "text": "Seeks sensory experiences"},
]



class ChildAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eye_contact = db.Column(db.Integer, nullable=False)
    response_to_name = db.Column(db.Integer, nullable=False)
    uses_gestures = db.Column(db.Integer, nullable=False)
    play_behavior = db.Column(db.Integer, nullable=False)
    verbal_communication = db.Column(db.Integer, nullable=False)
    social_smiling = db.Column(db.Integer, nullable=False)
    shared_interest = db.Column(db.Integer, nullable=False)
    follows_direction = db.Column(db.Integer, nullable=False)
    repetitive_behaviors = db.Column(db.Integer, nullable=False)
    routines_or_rituals = db.Column(db.Integer, nullable=False)
    intense_interests = db.Column(db.Integer, nullable=False)
    reacts_to_changes = db.Column(db.Integer, nullable=False)
    handles_frustration = db.Column(db.Integer, nullable=False)
    shows_empathy = db.Column(db.Integer, nullable=False)
    calming_strategies = db.Column(db.Integer, nullable=False)
    age_started_speaking = db.Column(db.Integer, nullable=True)
    uses_language = db.Column(db.Integer, nullable=False)
    imaginative_play = db.Column(db.Integer, nullable=False)
    unusual_speech_patterns = db.Column(db.Integer, nullable=False)
    unusual_reactions = db.Column(db.Integer, nullable=False)  # New field
    clothing_textures_intolerance = db.Column(db.Integer, nullable=False)  # New field
    seeks_sensory_experiences = db.Column(db.Integer, nullable=False)  # New field

def initialize_database():
    db.create_all()


@app.route("/", methods=['GET', 'POST'])
def questionnaire():
    if request.method == 'POST':
        # Collect scores from the questionnaire using the defined questions
        scores = [int(request.form[question['id']]) for question in QUESTIONS]
        total_score = sum(scores)

        # Create a new assessment entry in the database
        new_assessment = ChildAssessment(
            eye_contact=scores[0],
            response_to_name=scores[1],
            uses_gestures=scores[2],
            play_behavior=scores[3],
            verbal_communication=scores[4],
            social_smiling=scores[5],
            shared_interest=scores[6],
            follows_direction=scores[7],
            repetitive_behaviors=scores[8],
            routines_or_rituals=scores[9],
            intense_interests=scores[10],
            reacts_to_changes=scores[11],
            handles_frustration=scores[12],
            shows_empathy=scores[13],
            calming_strategies=scores[14],
            age_started_speaking=scores[15],  # Assuming this is handled correctly as an integer
            uses_language=scores[16],
            imaginative_play=scores[17],
            unusual_speech_patterns=scores[18],
            unusual_reactions=scores[19],
            clothing_textures_intolerance=scores[20],
            seeks_sensory_experiences=scores[21]
        )

        db.session.add(new_assessment)
        try:
            db.session.commit()
            return redirect(url_for('result', assessment_id=new_assessment.id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to commit to database: {e}")  # Log the error
            return str(e), 500


    return render_template("questions.html", questions=QUESTIONS)


@app.route("/result/<int:assessment_id>")
def result(assessment_id):
    assessment = db.session.get(ChildAssessment, assessment_id)

    if not assessment:
        return "Assessment not found", 404

    # Generate graphs
    generate_graphs(assessment)

    # Calculate the total score from the assessment
    total_score = sum([
        assessment.eye_contact,
        assessment.response_to_name,
        assessment.uses_gestures,
        assessment.play_behavior,
        assessment.verbal_communication,
        assessment.social_smiling,
        assessment.shared_interest,
        assessment.follows_direction,
        assessment.repetitive_behaviors,
        assessment.routines_or_rituals,
        assessment.intense_interests,
        assessment.reacts_to_changes,
        assessment.handles_frustration,
        assessment.shows_empathy,
        assessment.calming_strategies,
        assessment.uses_language,
        assessment.imaginative_play,
        assessment.unusual_speech_patterns,
        assessment.unusual_reactions,
        assessment.clothing_textures_intolerance,
        assessment.seeks_sensory_experiences
    ])

    # Determine likelihood based on the score
    likelihood = "Low likelihood of ASD"
    if total_score > 60:  # Assuming a maximum score of 105
        likelihood = "High likelihood of ASD"
    elif total_score > 40:
        likelihood = "Moderate likelihood of ASD"

    return render_template("result.html", score=total_score, likelihood=likelihood, assessment=assessment)


def generate_graphs(assessment):
    # Bar Chart
    questions = [question['text'] for question in QUESTIONS]
    scores = [getattr(assessment, question['id']) for question in QUESTIONS]

    plt.figure(figsize=(10, 6))
    plt.barh(questions, scores, color='skyblue')
    plt.xlabel('Score')
    plt.ylabel('Questions')
    plt.title('Scores for Each Question')
    plt.tight_layout()
    plt.savefig('static/bar_chart.png')

    # Pie Chart
    categories = ['Social & Communication', 'Behavioral Patterns', 'Language Development', 'Sensory Sensitivity',
                  'Emotional Regulation']

    # Extract scores for each category
    social_communication_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['eye_contact', 'response_to_name', 'uses_gestures', 'play_behavior']
    ]

    behavioral_patterns_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['repetitive_behaviors', 'routines_or_rituals', 'intense_interests', 'reacts_to_changes']
    ]

    language_development_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['age_started_speaking', 'uses_language', 'imaginative_play', 'unusual_speech_patterns']
    ]

    sensory_sensitivity_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['unusual_reactions', 'clothing_textures_intolerance', 'seeks_sensory_experiences']
    ]

    emotional_regulation_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['handles_frustration', 'shows_empathy', 'calming_strategies']
    ]

    # Calculate total scores for each category
    category_scores = [
        sum(social_communication_scores),
        sum(behavioral_patterns_scores),
        sum(language_development_scores),
        sum(sensory_sensitivity_scores),
        sum(emotional_regulation_scores)
    ]

    explode = (0.1, 0, 0, 0, 0)  # explode the first slice
    plt.figure(figsize=(8, 8))
    plt.pie(category_scores, explode=explode, labels=categories, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title('Distribution of Scores by Category')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    plt.savefig('static/pie_chart.png')

    # Histogram
    all_scores = [sum([getattr(assessment, question['id']) for question in QUESTIONS]) for assessment in ChildAssessment.query.all()]
    plt.figure(figsize=(10, 6))
    plt.hist(all_scores, bins=np.arange(0, 110, 10), color='orange', edgecolor='black')
    plt.xlabel('Total Score')
    plt.ylabel('Frequency')
    plt.title('Distribution of Total Scores')
    plt.tight_layout()
    plt.savefig('static/histogram.png')

    # Scatter Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(assessment.eye_contact, assessment.verbal_communication, color='green')
    plt.xlabel('Eye Contact')
    plt.ylabel('Verbal Communication')
    plt.title('Relationship between Eye Contact and Verbal Communication')
    plt.tight_layout()
    plt.savefig('static/scatter_plot.png')

    # Radar Chart
    categories = ['Social & Communication', 'Behavioral Patterns', 'Language Development', 'Sensory Sensitivity',
                  'Emotional Regulation']

    # Extract scores for each category
    social_communication_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['eye_contact', 'response_to_name', 'uses_gestures', 'play_behavior']
    ]

    behavioral_patterns_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['repetitive_behaviors', 'routines_or_rituals', 'intense_interests', 'reacts_to_changes']
    ]

    language_development_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['age_started_speaking', 'uses_language', 'imaginative_play', 'unusual_speech_patterns']
    ]

    sensory_sensitivity_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['unusual_reactions', 'clothing_textures_intolerance', 'seeks_sensory_experiences']
    ]

    emotional_regulation_scores = [
        getattr(assessment, question['id']) for question in QUESTIONS
        if question['id'] in ['handles_frustration', 'shows_empathy', 'calming_strategies']
    ]

    # Calculate average scores for each category
    category_scores = [
        sum(social_communication_scores) / len(social_communication_scores),
        sum(behavioral_patterns_scores) / len(behavioral_patterns_scores),
        sum(language_development_scores) / len(language_development_scores),
        sum(sensory_sensitivity_scores) / len(sensory_sensitivity_scores),
        sum(emotional_regulation_scores) / len(emotional_regulation_scores)
    ]

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.fill(angles, category_scores, color='skyblue', alpha=0.5)
    ax.plot(angles, category_scores, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(categories)
    plt.title('Radar Chart of Assessment Scores', size=20, color='blue', y=1.1)
    plt.tight_layout()
    plt.savefig('static/radar_chart.png')


@app.route('/api/assessment/<int:assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    assessment = ChildAssessment.query.get(assessment_id)
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404

    # Serialize the data to be JSON-friendly
    assessment_data = {
        'id': assessment.id,
        'eye_contact': assessment.eye_contact,
        'response_to_name': assessment.response_to_name,
        'uses_gestures': assessment.uses_gestures,
        'play_behavior': assessment.play_behavior,
        'verbal_communication': assessment.verbal_communication,
        'social_smiling': assessment.social_smiling,
        'shared_interest': assessment.shared_interest,
        'follows_direction': assessment.follows_direction,
        'repetitive_behaviors': assessment.repetitive_behaviors,
        'routines_or_rituals': assessment.routines_or_rituals,
        'intense_interests': assessment.intense_interests,
        'reacts_to_changes': assessment.reacts_to_changes,
        'handles_frustration': assessment.handles_frustration,
        'shows_empathy': assessment.shows_empathy,
        'calming_strategies': assessment.calming_strategies,
        'age_started_speaking': assessment.age_started_speaking,
        'uses_language': assessment.uses_language,
        'imaginative_play': assessment.imaginative_play,
        'unusual_speech_patterns': assessment.unusual_speech_patterns,
        'unusual_reactions': assessment.unusual_reactions,
        'clothing_textures_intolerance': assessment.clothing_textures_intolerance,
        'seeks_sensory_experiences': assessment.seeks_sensory_experiences
    }

    return jsonify(assessment_data)



# At the end of your app.py

if __name__ == "__main__":
 
    app.run(debug=False, host='0.0.0.0', port=80)  # Run the Flask development server



