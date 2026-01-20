Phase 6: Low Priority Cleanup Plan                                             
                                                                                
 Overview                                                                       
                                                                                
 This phase addresses minor code quality issues from the PeanutChat audit. All  
 changes are low-risk documentation or minor code fixes.                        
                                                                                
 Files to Modify                                                                
                                                                                
 1. /home/tech/PeanutChat/static/js/settings.js                                 
                                                                                
 Issue: Line 183-185 has a useless check - typeof knowledgeManager !==          
 'undefined' always evaluates to true because knowledgeManager is a global      
 constant defined at the bottom of knowledge.js (line 236).                     
                                                                                
 Current code (lines 182-186):                                                  
 // Initialize knowledge base manager                                           
 if (typeof knowledgeManager !== 'undefined') {                                 
     knowledgeManager.init();                                                   
 }                                                                              
                                                                                
 Change: Remove the unnecessary check and call init() directly:                 
 // Initialize knowledge base manager                                           
 knowledgeManager.init();                                                       
                                                                                
 ---                                                                            
 2. /home/tech/PeanutChat/app/services/database.py                              
                                                                                
 Issue: Migration 002 creates TTS columns that are later removed by migration   
 006. Adding documentation makes this clearer for future developers.            
                                                                                
 Change: Update the docstring for _migration_002_create_user_settings method    
 (line 147) to document this:                                                   
 def _migration_002_create_user_settings(self):                                 
     """Create user_settings table.                                             
                                                                                
     NOTE: This migration creates TTS columns that are no longer used.          
     Migration 006 (_migration_006_remove_tts_columns) removes them.            
     """                                                                        
                                                                                
 ---                                                                            
 3. /home/tech/PeanutChat/app/services/knowledge_store.py                       
                                                                                
 Issue: Embeddings are stored as JSON strings, which is less efficient than     
 BLOB for large datasets. Adding a TODO comment documents this technical debt.  
                                                                                
 Change: Add a TODO comment in add_chunk() method (before line 89):             
 def add_chunk(                                                                 
     self,                                                                      
     document_id: str,                                                          
     chunk_index: int,                                                          
     content: str,                                                              
     embedding: List[float]                                                     
 ) -> str:                                                                      
     """Add a chunk with its embedding"""                                       
     chunk_id = str(uuid.uuid4())                                               
     # TODO: Consider using BLOB for embeddings instead of JSON string.         
     # JSON works but is less efficient for large datasets with many vectors.   
     embedding_json = json.dumps(embedding)                                     
                                                                                
 ---                                                                            
 Verification                                                                   
                                                                                
 After making changes, verify no runtime errors:                                
 python -c "from app.services.database import get_database; db =                
 get_database(); print('DB OK')"                                                
 python -c "from app.services.knowledge_store import get_knowledge_store; ks =  
 get_knowledge_store(); print('KnowledgeStore OK')"                             
                                                                                
 Test the settings modal opens correctly by:                                    
 1. Start the application                                                       
 2. Open settings modal                                                         
 3. Confirm no JavaScript errors in console                                     
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
                                                                                
