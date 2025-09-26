-- Création de la table Feedback_user
CREATE TABLE Feedback_user (
    id_feedback_user SERIAL PRIMARY KEY,
    feedback boolean NOT NULL,
    date_feedback DATE NOT NULL,
    resultat_prediction float NOT NULL,
    input_user text NOT NULL,
    inference_time_ms float,
    success boolean
);

-- Migration idempotente pour ajouter colonnes si table déjà créée
ALTER TABLE IF EXISTS Feedback_user
    ADD COLUMN IF NOT EXISTS inference_time_ms float;
ALTER TABLE IF EXISTS Feedback_user
    ADD COLUMN IF NOT EXISTS success boolean;