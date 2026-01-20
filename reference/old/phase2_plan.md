Phase 2: Concurrency & Data Integrity Fixes                                    
                                                                                
 Problem                                                                        
                                                                                
 PeanutChat uses threading.Lock() in ConversationStore but FastAPI is async.    
 This causes race conditions under concurrent requests because threading.Lock() 
  blocks the entire event loop, and doesn't properly protect against            
 interleaved async operations.                                                  
                                                                                
 Solution                                                                       
                                                                                
 Convert ConversationStore to use asyncio.Lock() and make all write methods     
 async.                                                                         
                                                                                
 ---                                                                            
 Task 1: Convert ConversationStore to Async                                     
                                                                                
 File: app/services/conversation_store.py                                       
                                                                                
 Step 1.1: Change import (line 9)                                               
                                                                                
 # FROM:                                                                        
 import threading                                                               
                                                                                
 # TO:                                                                          
 import asyncio                                                                 
                                                                                
 Step 1.2: Change lock initialization (line 76)                                 
                                                                                
 # FROM:                                                                        
 self._lock = threading.Lock()                                                  
                                                                                
 # TO:                                                                          
 self._lock = asyncio.Lock()                                                    
                                                                                
 Step 1.3: Convert _save() to async (lines 91-95)                               
                                                                                
 # FROM:                                                                        
 def _save(self, conversation: Conversation):                                   
                                                                                
 # TO:                                                                          
 async def _save(self, conversation: Conversation):                             
                                                                                
 Step 1.4: Convert create() to async (lines 97-113)                             
                                                                                
 # Change `def create` → `async def create`                                     
 # Change `with self._lock:` → `async with self._lock:`                         
 # Change `self._save(conv)` → `await self._save(conv)`                         
                                                                                
 Step 1.5: Convert add_message() to async (lines 166-195)                       
                                                                                
 # Change `def add_message` → `async def add_message`                           
 # Change `with self._lock:` → `async with self._lock:`                         
 # Change `self._save(conv)` → `await self._save(conv)`                         
                                                                                
 Step 1.6: Convert update_message() to async (lines 197-215)                    
                                                                                
 # Change `def update_message` → `async def update_message`                     
 # Change `with self._lock:` → `async with self._lock:`                         
 # Change `self._save(conv)` → `await self._save(conv)`                         
                                                                                
 Step 1.7: Convert fork_at_message() to async (lines 217-280)                   
                                                                                
 # Change `def fork_at_message` → `async def fork_at_message`                   
 # Change `with self._lock:` → `async with self._lock:`                         
 # Change `self._save(new_conv)` → `await self._save(new_conv)`                 
                                                                                
 Step 1.8: Convert delete() to async (lines 282-292)                            
                                                                                
 # Change `def delete` → `async def delete`                                     
 # Change `with self._lock:` → `async with self._lock:`                         
                                                                                
 Step 1.9: Convert rename() to async (lines 294-304)                            
                                                                                
 # Change `def rename` → `async def rename`                                     
 # Change `with self._lock:` → `async with self._lock:`                         
 # Change `self._save(conv)` → `await self._save(conv)`                         
                                                                                
 Step 1.10: Convert clear_messages() to async (lines 322-333)                   
                                                                                
 # Change `def clear_messages` → `async def clear_messages`                     
 # Change `with self._lock:` → `async with self._lock:`                         
 # Change `self._save(conv)` → `await self._save(conv)`                         
                                                                                
 Methods that stay synchronous (read-only, no lock):                            
                                                                                
 - get() - line 115                                                             
 - list_for_user() - line 124                                                   
 - list_all() - line 146                                                        
 - get_messages_for_api() - line 306                                            
 - search_conversations() - line 335                                            
                                                                                
 ---                                                                            
 Task 2: Update Call Sites in chat.py                                           
                                                                                
 File: app/routers/chat.py                                                      
                                                                                
 Call sites that need await:                                                    
 ┌──────┬───────────────────┬───────────┐                                       
 │ Line │      Method       │  Change   │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 126  │ create()          │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 136  │ create()          │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 203  │ add_message()     │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 317  │ add_message()     │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 391  │ add_message()     │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 407  │ add_message()     │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 458  │ create()          │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 478  │ delete()          │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 494  │ rename()          │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 506  │ clear_messages()  │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 523  │ update_message()  │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 541  │ fork_at_message() │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 676  │ add_message()     │ Add await │                                       
 ├──────┼───────────────────┼───────────┤                                       
 │ 734  │ clear_messages()  │ Add await │                                       
 └──────┴───────────────────┴───────────┘                                       
 Direct lock access (lines 593-595):                                            
                                                                                
 # FROM:                                                                        
 with conversation_store._lock:                                                 
     conv.messages = conv.messages[:msg_index]                                  
     conversation_store._save(conv)                                             
                                                                                
 # TO:                                                                          
 async with conversation_store._lock:                                           
     conv.messages = conv.messages[:msg_index]                                  
     await conversation_store._save(conv)                                       
                                                                                
 No changes needed for these read-only calls:                                   
                                                                                
 - Lines 132, 465, 475, 491, 503, 520, 538, 561, 720, 732: .get() calls         
 - Lines 165, 608, 723: .get_messages_for_api() calls                           
 - Line 451: .list_for_user() call                                              
                                                                                
 ---                                                                            
 Task 3: Verify tool_executor.py                                                
                                                                                
 File: app/services/tool_executor.py                                            
                                                                                
 Line 502: search_conversations() is read-only and stays synchronous - no       
 changes needed.                                                                
                                                                                
 ---                                                                            
 Task 4: Improve Load Error Handling                                            
                                                                                
 File: app/services/conversation_store.py (lines 80-89)                         
                                                                                
 Replace _load_all() method with better error handling:                         
                                                                                
 def _load_all(self):                                                           
     """Load all conversations into cache"""                                    
     failed_files = []                                                          
     for file_path in self.storage_dir.glob("*.json"):                          
         try:                                                                   
             with open(file_path) as f:                                         
                 data = json.load(f)                                            
                 conv = Conversation.from_dict(data)                            
                 self._cache[conv.id] = conv                                    
         except json.JSONDecodeError as e:                                      
             logger.error(f"Corrupt JSON in {file_path}: {e}")                  
             failed_files.append(file_path)                                     
             # Move to backup                                                   
             backup_path = file_path.with_suffix('.json.corrupt')               
             file_path.rename(backup_path)                                      
             logger.warning(f"Moved corrupt file to {backup_path}")             
         except Exception as e:                                                 
             logger.error(f"Error loading conversation {file_path}: {e}")       
             failed_files.append(file_path)                                     
                                                                                
     if failed_files:                                                           
         logger.warning(f"Failed to load {len(failed_files)} conversations")    
                                                                                
 ---                                                                            
 Files Modified                                                                 
                                                                                
 1. app/services/conversation_store.py - Convert to asyncio.Lock, make methods  
 async                                                                          
 2. app/routers/chat.py - Add await to 14 call sites + fix direct lock access   
 3. app/services/tool_executor.py - No changes needed (read-only method)        
                                                                                
 ---                                                                            
 Verification                                                                   
                                                                                
 cd /home/tech/PeanutChat                                                       
                                                                                
 # 1. Test asyncio.Lock is used                                                 
 grep -n "asyncio.Lock" app/services/conversation_store.py                      
 # Expected: Should show line ~76                                               
                                                                                
 # 2. Verify async def for write methods                                        
 grep -n "async def" app/services/conversation_store.py                         
 # Expected: 8 methods (_save, create, add_message, update_message,             
 fork_at_message, delete, rename, clear_messages)                               
                                                                                
 # 3. Count await calls in chat.py                                              
 grep -c "await conversation_store\." app/routers/chat.py                       
 # Expected: 14                                                                 
                                                                                
 # 4. Test app imports successfully                                             
 source venv/bin/activate && python -c "from app.main import app; print('OK')"  
                                                                                
 # 5. Run the app and test manually                                             
 ./start_peanutchat.sh                                                          
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
                                                                                
 Requested permissions:                                                         
   · Bash(prompt: run Python import test)                                       
   · Bash(prompt: run grep to verify changes)         
