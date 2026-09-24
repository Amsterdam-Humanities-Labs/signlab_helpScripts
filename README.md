# signlab_helpScripts
Helper scripts from the core server's `/web/helpScripts`: a few live endpoints and jobs, and many one-off tools.

## What it does
- Live endpoints: `emptyVideoTop.php` (clear recorded-take markers for a user and theme; called by the studio pages in [signlab_camera-control](https://github.com/Amsterdam-Humanities-Labs/signlab_camera-control)), `updateVideoRow.php`, `deleteVideoRow.php`, `fetchVideoTop.php` (video rows in `CameraRecords` and `matched_transcriptions`).
- Server jobs: `convert.py` (FFmpeg transcode to `studioFilesMini`, thumbnails), `mysqlBackup.php` (hourly backups, 14-day hourly and 1-year daily retention), `zinBackup.py` (ZIP of sentence EAF/SRT files), `check_studiofiles.py` (move misfiled raw videos).
- Signbank tools: `signBankCSVDownloader.py` (download the gloss package, convert it to JSON), `signbankGlosExists.py`, `sensesChecker.py`, `fonoChecker.py`, `glosSyntaxChecker.py`, `signbank/` (inspect and convert `glosses.json`).
- Phonology (fono) tools: `createFonoArray.py`, `panono.py`, `translateFono.py`. They read the saved Signbank lists in `*NL.html` / `*EN.html`.
- Blender and mocap: `addRigify.py`, `blenderPlugins.py`, `fbxBatchConvert.py`, `freemocapAutoRetargetBlender/` (own README).
- The rest are one-off fixes and tests (`test*`, `fix*`, `batchHelper*.py`, `nme_video*.py`, ...). Check a script before you run it: many write to the database.

## Where it runs
The core server: `/web/helpScripts`, URL `https://signcollect.nl/helpScripts/`.
The server runs its own copy. This repo is a backup of that code and is not deployed yet.

## Status
Production (copy of the live code, 2026-09-22). See [signlab_signcollect-stack#35](https://github.com/Amsterdam-Humanities-Labs/signlab_signcollect-stack/issues/35).

## How to run or deploy
Not deployed from here. Scripts run by hand on the core server, for example:
```
cd /web/helpScripts && python3 signBankCSVDownloader.py
```
[signlab_pythonCron](https://github.com/Amsterdam-Humanities-Labs/signlab_pythonCron) now schedules its own copies of the four server jobs (`video_converter.py`, `mysql_backup.php`, `zin_backup.py`, `move_studiofiles.py`). Older docs still name the files here.

## Configuration
- PHP: `../mysql_config.php` (not in git). `export_matched_transcriptions.php` uses `/web/mysql_config.php`.
- Python: environment variables `DB_PASS`, `SIGNBANK_API_KEY`, `SIGNBANK_CSRFTOKEN`, `SIGNBANK_SESSIONID`, `OPENROUTER_API_KEY`. Some scripts connect to host `signlab-db`, others to `localhost`.
- A few Signbank scripts still hold a hardcoded API token. Move it to `SIGNBANK_API_KEY` before reuse.
- Paths are absolute: `/web/helpScripts`, `/web/gebarenoverleg_media/studioFiles`, `/web/glosses_transformed.json`.
- `check_studiofiles.py`, `zinBackup.py` and `mysqlBackup.php` load the client monitor from `/home/gomer/pythonCron`.

## Dependencies
- MySQL database `admin_gebarenoverleg`; Signbank (`signbank.cls.ru.nl`); FFmpeg; Blender for the Blender scripts.
- Services on `leffe.science.uva.nl:8043` (`signBankAPI`, `fbx2glb`, `autoUpdater.php`).
- `convert.py` imports `renderServer.video_api_client`, which is not in this repo.

## License and citation

Apache License 2.0, copyright University of Amsterdam: see [LICENSE](LICENSE) and
[NOTICE](NOTICE). You may use it, also commercially, as long as you credit
Gomer Otterspeer / University of Amsterdam as the source. To cite it, use
[CITATION.cff](CITATION.cff) (the *Cite this repository* button on GitHub) or the DOI [10.21942/uva.33980335](https://doi.org/10.21942/uva.33980335).
