-- Création de la table Feedback_user
CREATE TABLE Feedback_user (
    id_feedback_user SERIAL PRIMARY KEY,
    feedback boolean NOT NULL,
    date_feedback DATE NOT NULL,
    resultat_prediction float NOT NULL,
    input_user text NOT NULL
);