SELECT *
FROM nmm_data
WHERE (signbank_id IS NULL OR signbank_id = '')
  AND glos IN (
    SELECT glos
    FROM nmm_data
    GROUP BY glos
    HAVING COUNT(CASE WHEN signbank_id IS NOT NULL AND signbank_id <> '' THEN 1 END) > 0
  ) AND type = 'ready' ORDER BY `signbank_id` DESC



  1) Vind dups in nmm_data
  2) VARIATIE-B heeft twee verschillende id's, beide hebben rows in matched_transcriptions
  3) pak de eerste id in nmm_data en verwijder de rest in nmm_data
  4) update l_transcription, m_transcription, r_transcription, a_transcription, b_transcription in matched_transcriptions naar die eerste id op basis van de rest van de ids van nmm_data

  