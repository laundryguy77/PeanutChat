Phase 4: Dependency & Schema Cleanup                                           
                                                                                
 Problem                                                                        
                                                                                
 TTS/STT features were planned but never implemented. The dependencies remain   
 in requirements.txt causing bloated container images (~10GB+). The database    
 schema also has dead TTS columns in user_settings.                             
                                                                                
 Solution                                                                       
                                                                                
 1. Remove unused dependencies from requirements.txt                            
 2. Add migration 006 to remove TTS columns from user_settings                  
                                                                                
 ---                                                                            
 Task 1: Remove Unused Dependencies                                             
                                                                                
 File: app/services/../requirements.txt (root)                                  
                                                                                
 Remove these lines (15-23):                                                    
                                                                                
 # Speech-to-Text (Parakeet)                                                    
 nemo_toolkit[asr]>=2.0.0                                                       
 soundfile>=0.12.0                                                              
                                                                                
 # Text-to-Speech (CSM)                                                         
 tokenizers>=0.15.0                                                             
 huggingface_hub>=0.20.0                                                        
 silentcipher>=1.0.0                                                            
 moshi>=0.1.0                                                                   
                                                                                
 Verification: None of these packages are imported anywhere in the codebase.    
                                                                                
 ---                                                                            
 Task 2: Add Migration to Remove TTS Columns                                    
                                                                                
 File: app/services/database.py                                                 
                                                                                
 Step 2.1: Add migration 006 to the migrations list (line 103)                  
                                                                                
 migrations = [                                                                 
     ("001_create_users", self._migration_001_create_users),                    
     ("002_create_user_settings", self._migration_002_create_user_settings),    
     ("003_create_conversations", self._migration_003_create_conversations),    
     ("004_create_documents", self._migration_004_create_documents),            
     ("005_create_chunks", self._migration_005_create_chunks),                  
     ("006_remove_tts_columns", self._migration_006_remove_tts_columns),  # ADD 
 ]                                                                              
                                                                                
 Step 2.2: Add new migration method after _migration_005_create_chunks()        
                                                                                
 def _migration_006_remove_tts_columns(self):                                   
     """Remove deprecated TTS columns from user_settings"""                     
     # SQLite doesn't support DROP COLUMN directly, recreate the table          
     self.execute("""                                                           
         CREATE TABLE user_settings_new (                                       
             user_id INTEGER PRIMARY KEY,                                       
             model TEXT,                                                        
             temperature REAL,                                                  
             top_p REAL,                                                        
             top_k INTEGER,                                                     
             num_ctx INTEGER,                                                   
             repeat_penalty REAL,                                               
             persona TEXT,                                                      
             FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE       
         )                                                                      
     """)                                                                       
                                                                                
     # Copy data (excluding TTS columns)                                        
     self.execute("""                                                           
         INSERT INTO user_settings_new (user_id, model, temperature, top_p,     
 top_k, num_ctx, repeat_penalty, persona)                                       
         SELECT user_id, model, temperature, top_p, top_k, num_ctx,             
 repeat_penalty, persona                                                        
         FROM user_settings                                                     
     """)                                                                       
                                                                                
     # Drop old table and rename                                                
     self.execute("DROP TABLE user_settings")                                   
     self.execute("ALTER TABLE user_settings_new RENAME TO user_settings")      
                                                                                
 Note: We do NOT modify migration 002 - that would break existing databases.    
 Migration 006 handles cleanup for existing installs. New installs will run     
 both migrations (002 creates with TTS columns, 006 removes them).              
                                                                                
 ---                                                                            
 Files Modified                                                                 
                                                                                
 1. requirements.txt - Remove 8 lines (TTS/STT dependencies)                    
 2. app/services/database.py - Add migration 006 to remove TTS columns          
                                                                                
 ---                                                                            
 Verification                                                                   
                                                                                
 cd /home/tech/PeanutChat                                                       
                                                                                
 # 1. Verify dependencies removed                                               
 grep -E "nemo|soundfile|tokenizers|huggingface|silentcipher|moshi"             
 requirements.txt                                                               
 # Expected: No output                                                          
                                                                                
 # 2. Test app imports successfully                                             
 ./venv/bin/python3 -c "from app.main import app; print('OK')"                  
                                                                                
 # 3. Verify migration runs (check logs)                                        
 ./venv/bin/python3 -c "from app.services.database import get_database; db =    
 get_database(); print('Migration OK')"                                         
                                                                                
 # 4. Verify TTS columns removed from user_settings                             
 ./venv/bin/python3 -c "                                                        
 from app.services.database import get_database                                 
 db = get_database()                                                            
 cols = [row[1] for row in db.fetchall('PRAGMA table_info(user_settings)')]     
 print('Columns:', cols)                                                        
 assert 'tts_enabled' not in cols, 'TTS columns still present'                  
 print('TTS columns removed successfully')                                      
 "                                                                              
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
                                                                                
 Requested permissions:                                                         
   · Bash(prompt: run python scripts for verification)    
