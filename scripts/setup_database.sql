-- Script de création des tables pour le stockage des images d'utilisateurs

-- Table pour stocker les métadonnées des images d'utilisateurs
CREATE TABLE IF NOT EXISTS user_images (
    id_image SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    image_width INTEGER,
    image_height INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100), -- Optionnel pour identifier l'utilisateur
    session_id VARCHAR(100), -- Pour grouper les images par session
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processed, error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour lier les images aux feedbacks
CREATE TABLE IF NOT EXISTS image_feedback_link (
    id_link SERIAL PRIMARY KEY,
    id_image INTEGER REFERENCES user_images(id_image) ON DELETE CASCADE,
    id_feedback_user INTEGER REFERENCES feedback_user(id_feedback_user) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_image, id_feedback_user)
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_images_uploaded_at ON user_images(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_user_images_processed ON user_images(is_processed);

-- Vue pour les statistiques des images utilisateurs
CREATE OR REPLACE VIEW user_images_stats AS
SELECT 
    DATE(uploaded_at) as upload_date,
    COUNT(*) as total_images,
    COUNT(CASE WHEN is_processed = TRUE THEN 1 END) as processed_images,
    COUNT(CASE WHEN processing_status = 'error' THEN 1 END) as error_images,
    AVG(file_size) as avg_file_size,
    SUM(file_size) as total_storage_used
FROM user_images
GROUP BY DATE(uploaded_at)
ORDER BY upload_date DESC;
