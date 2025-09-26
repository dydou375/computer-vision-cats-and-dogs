-- Script pour ajouter le nom de fichier à la table feedback_user existante

-- Ajouter une colonne filename à la table feedback_user
ALTER TABLE feedback_user 
ADD COLUMN IF NOT EXISTS filename VARCHAR(255);

-- Ajouter un index sur la colonne filename pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_feedback_user_filename ON feedback_user(filename);
