Phase 3: Frontend UX & Code Quality - Implementation Plan                                                                                                        
                                                                                                                                                                  
 Overview                                                                                                                                                         
                                                                                                                                                                  
 Fix frontend UX issues and add token refresh mechanism to PeanutChat.                                                                                            
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 3.1: Filter Embedding Models from Dropdown                                                                                                                  
                                                                                                                                                                  
 File: static/js/app.js (lines 391-439)                                                                                                                           
                                                                                                                                                                  
 Problem: Users can select embedding models (nomic-embed-text, snowflake-arctic-embed) which cannot chat.                                                         
                                                                                                                                                                  
 Change: In loadModels() method, filter models before rendering:                                                                                                  
                                                                                                                                                                  
 // After line 397: const data = await response.json();                                                                                                           
 // Add filter before rendering:                                                                                                                                  
 const chatModels = (data.models || []).filter(model => {                                                                                                         
     const name = model.name.toLowerCase();                                                                                                                       
     return !name.includes('embed');                                                                                                                              
 });                                                                                                                                                              
                                                                                                                                                                  
 Then change line 402 from:                                                                                                                                       
 if (data.models && data.models.length > 0) {                                                                                                                     
     data.models.forEach(model => {                                                                                                                               
 To:                                                                                                                                                              
 if (chatModels.length > 0) {                                                                                                                                     
     chatModels.forEach(model => {                                                                                                                                
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 3.2: Load Capabilities Before Model Selection                                                                                                               
                                                                                                                                                                  
 File: static/js/app.js (lines 81-89)                                                                                                                             
                                                                                                                                                                  
 Problem: Users don't see capabilities until after selecting model.                                                                                               
                                                                                                                                                                  
 Change: Reorder calls in initializeApp():                                                                                                                        
                                                                                                                                                                  
 From:                                                                                                                                                            
 await this.loadModels();                                                                                                                                         
 await this.settingsManager.loadSettings();                                                                                                                       
 await this.loadModelCapabilities();                                                                                                                              
                                                                                                                                                                  
 To:                                                                                                                                                              
 await this.loadModelCapabilities();                                                                                                                              
 await this.settingsManager.loadSettings();                                                                                                                       
 await this.loadModels();                                                                                                                                         
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 3.3: Add Global Error Handler                                                                                                                               
                                                                                                                                                                  
 File: static/js/app.js                                                                                                                                           
                                                                                                                                                                  
 Change 1: Add showError method to App class (after line 259, after handleLogout):                                                                                
                                                                                                                                                                  
 showError(message) {                                                                                                                                             
     const toast = document.createElement('div');                                                                                                                 
     toast.className = 'fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2 rounded shadow-lg z-50';                                                           
     toast.textContent = message;                                                                                                                                 
     document.body.appendChild(toast);                                                                                                                            
     setTimeout(() => toast.remove(), 5000);                                                                                                                      
 }                                                                                                                                                                
                                                                                                                                                                  
 Change 2: In loadModels() catch block (line 436), add user feedback:                                                                                             
                                                                                                                                                                  
 From:                                                                                                                                                            
 } catch (error) {                                                                                                                                                
     console.error('Failed to load models:', error);                                                                                                              
     select.innerHTML = '<option value="">Failed to load</option>';                                                                                               
 }                                                                                                                                                                
                                                                                                                                                                  
 To:                                                                                                                                                              
 } catch (error) {                                                                                                                                                
     console.error('Failed to load models:', error);                                                                                                              
     select.innerHTML = '<option value="">Failed to load</option>';                                                                                               
     this.showError('Failed to load models. Check Ollama connection.');                                                                                           
 }                                                                                                                                                                
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 3.4: Remove Debug Console.log Statements                                                                                                                    
                                                                                                                                                                  
 File: static/js/chat.js                                                                                                                                          
                                                                                                                                                                  
 Lines to DELETE entirely (9 lines):                                                                                                                              
 ┌──────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐                               
 │ Line │                                                          Code                                                           │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 193  │ console.log('Creating action buttons for message:', { role, msgId, contentPreview: messageContent?.substring(0, 30) }); │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 201  │ console.log('User copy button clicked!');                                                                               │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 226  │ console.log('Assistant copy button clicked!');                                                                          │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 239  │ console.log('Regenerate button clicked!', msgId);                                                                       │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 534  │ console.log('regenerateResponse called with messageId:', messageId);                                                    │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 536  │ console.log('Blocked: already streaming');                                                                              │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 541  │ console.log('Conversation ID:', convId);                                                                                │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 543  │ console.log('Blocked: no conversation ID');                                                                             │                               
 ├──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤                               
 │ 548  │ console.log('Fetching regenerate endpoint...');                                                                         │                               
 └──────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘                               
 ---                                                                                                                                                              
 Task 3.5: Parallel File Uploads                                                                                                                                  
                                                                                                                                                                  
 File: static/js/knowledge.js (lines 159-208)                                                                                                                     
                                                                                                                                                                  
 Problem: Files upload sequentially.                                                                                                                              
                                                                                                                                                                  
 Replace uploadFiles() method with:                                                                                                                               
                                                                                                                                                                  
 async uploadFiles(files) {                                                                                                                                       
     const progressDiv = document.getElementById('kb-upload-progress');                                                                                           
     const statusSpan = document.getElementById('kb-upload-status');                                                                                              
                                                                                                                                                                  
     if (progressDiv) progressDiv.classList.remove('hidden');                                                                                                     
     if (statusSpan) statusSpan.textContent = `Uploading ${files.length} file(s)...`;                                                                             
                                                                                                                                                                  
     // Filter oversized files first                                                                                                                              
     const validFiles = files.filter(file => {                                                                                                                    
         if (file.size > 10 * 1024 * 1024) {                                                                                                                      
             alert(`File "${file.name}" exceeds 10MB limit`);                                                                                                     
             return false;                                                                                                                                        
         }                                                                                                                                                        
         return true;                                                                                                                                             
     });                                                                                                                                                          
                                                                                                                                                                  
     // Upload all valid files in parallel                                                                                                                        
     const uploadPromises = validFiles.map(async (file) => {                                                                                                      
         try {                                                                                                                                                    
             const formData = new FormData();                                                                                                                     
             formData.append('file', file);                                                                                                                       
                                                                                                                                                                  
             const response = await fetch('/api/knowledge/upload', {                                                                                              
                 method: 'POST',                                                                                                                                  
                 credentials: 'include',                                                                                                                          
                 body: formData                                                                                                                                   
             });                                                                                                                                                  
                                                                                                                                                                  
             const result = await response.json();                                                                                                                
             return { file: file.name, success: response.ok, result };                                                                                            
         } catch (error) {                                                                                                                                        
             console.error(`Upload error for ${file.name}:`, error);                                                                                              
             return { file: file.name, success: false, error };                                                                                                   
         }                                                                                                                                                        
     });                                                                                                                                                          
                                                                                                                                                                  
     const results = await Promise.all(uploadPromises);                                                                                                           
                                                                                                                                                                  
     // Report failures                                                                                                                                           
     const failures = results.filter(r => !r.success);                                                                                                            
     if (failures.length > 0) {                                                                                                                                   
         alert(`Failed to upload: ${failures.map(f => f.file).join(', ')}`);                                                                                      
     }                                                                                                                                                            
                                                                                                                                                                  
     if (progressDiv) progressDiv.classList.add('hidden');                                                                                                        
                                                                                                                                                                  
     // Refresh stats and document list                                                                                                                           
     await this.loadStats();                                                                                                                                      
     await this.loadDocuments();                                                                                                                                  
 }                                                                                                                                                                
                                                                                                                                                                  
 ---                                                                                                                                                              
 Task 3.6: Add Token Refresh Mechanism                                                                                                                            
                                                                                                                                                                  
 Backend: app/routers/auth.py                                                                                                                                     
                                                                                                                                                                  
 Add import at top (line 2):                                                                                                                                      
 from fastapi import APIRouter, HTTPException, status, Response, Depends, Request                                                                                 
                                                                                                                                                                  
 Add endpoint after /logout (after line 85):                                                                                                                      
                                                                                                                                                                  
 @router.post("/refresh")                                                                                                                                         
 async def refresh_token(request: Request, response: Response):                                                                                                   
     """Refresh the access token using existing valid token"""                                                                                                    
     from jose import jwt, ExpiredSignatureError, JWTError                                                                                                        
                                                                                                                                                                  
     token = request.cookies.get("access_token")                                                                                                                  
     if not token:                                                                                                                                                
         raise HTTPException(status_code=401, detail="No token provided")                                                                                         
                                                                                                                                                                  
     auth_service = get_auth_service()                                                                                                                            
                                                                                                                                                                  
     try:                                                                                                                                                         
         payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])                                                                        
         user_id = int(payload.get("sub"))                                                                                                                        
         username = payload.get("username")                                                                                                                       
                                                                                                                                                                  
         # Issue new token with fresh expiration                                                                                                                  
         new_token = auth_service.create_access_token(user_id, username)                                                                                          
                                                                                                                                                                  
         response.set_cookie(                                                                                                                                     
             key="access_token",                                                                                                                                  
             value=new_token,                                                                                                                                     
             httponly=True,                                                                                                                                       
             secure=config.COOKIE_SECURE,                                                                                                                         
             samesite="lax",                                                                                                                                      
             max_age=60 * 60 * 24  # 24 hours                                                                                                                     
         )                                                                                                                                                        
         return {"message": "Token refreshed"}                                                                                                                    
     except ExpiredSignatureError:                                                                                                                                
         raise HTTPException(status_code=401, detail="Token expired - please login again")                                                                        
     except JWTError:                                                                                                                                             
         raise HTTPException(status_code=401, detail="Invalid token")                                                                                             
                                                                                                                                                                  
 Frontend: static/js/auth.js                                                                                                                                      
                                                                                                                                                                  
 Step 1: Add refreshInterval to constructor (line 9):                                                                                                             
 constructor() {                                                                                                                                                  
     this.user = null;                                                                                                                                            
     this.token = null;                                                                                                                                           
     this.onAuthChange = null;                                                                                                                                    
     this.refreshInterval = null;                                                                                                                                 
 }                                                                                                                                                                
                                                                                                                                                                  
 Step 2: Add three new methods after init() (after line 32):                                                                                                      
                                                                                                                                                                  
 startTokenRefresh() {                                                                                                                                            
     this.stopTokenRefresh();                                                                                                                                     
     // Refresh every 20 minutes (token expires in 24 hours)                                                                                                      
     this.refreshInterval = setInterval(() => this.refreshToken(), 20 * 60 * 1000);                                                                               
 }                                                                                                                                                                
                                                                                                                                                                  
 stopTokenRefresh() {                                                                                                                                             
     if (this.refreshInterval) {                                                                                                                                  
         clearInterval(this.refreshInterval);                                                                                                                     
         this.refreshInterval = null;                                                                                                                             
     }                                                                                                                                                            
 }                                                                                                                                                                
                                                                                                                                                                  
 async refreshToken() {                                                                                                                                           
     try {                                                                                                                                                        
         const response = await fetch('/api/auth/refresh', {                                                                                                      
             method: 'POST',                                                                                                                                      
             credentials: 'include'                                                                                                                               
         });                                                                                                                                                      
         if (!response.ok) {                                                                                                                                      
             console.warn('Token refresh failed, logging out');                                                                                                   
             this.stopTokenRefresh();                                                                                                                             
             await this.logout();                                                                                                                                 
         }                                                                                                                                                        
     } catch (error) {                                                                                                                                            
         console.error('Token refresh error:', error);                                                                                                            
     }                                                                                                                                                            
 }                                                                                                                                                                
                                                                                                                                                                  
 Step 3: Call startTokenRefresh() after successful auth:                                                                                                          
 - In init() after this.user = await response.json(); (line 23)                                                                                                   
 - In register() after this.token = data.access_token; (line 58)                                                                                                  
 - In login() after this.token = data.access_token; (line 83)                                                                                                     
                                                                                                                                                                  
 Step 4: Call stopTokenRefresh() at start of:                                                                                                                     
 - logout() method (line 91)                                                                                                                                      
 - deleteAccount() method (line 147)                                                                                                                              
                                                                                                                                                                  
 ---                                                                                                                                                              
 Files Summary                                                                                                                                                    
 ┌────────────────────────┬─────────────────────────────────────────────────────────┐                                                                             
 │          File          │                         Changes                         │                                                                             
 ├────────────────────────┼─────────────────────────────────────────────────────────┤                                                                             
 │ static/js/app.js       │ Filter embed models, reorder init, add showError method │                                                                             
 ├────────────────────────┼─────────────────────────────────────────────────────────┤                                                                             
 │ static/js/chat.js      │ Remove 9 console.log statements                         │                                                                             
 ├────────────────────────┼─────────────────────────────────────────────────────────┤                                                                             
 │ static/js/knowledge.js │ Parallel file uploads                                   │                                                                             
 ├────────────────────────┼─────────────────────────────────────────────────────────┤                                                                             
 │ static/js/auth.js      │ Add token refresh mechanism                             │                                                                             
 ├────────────────────────┼─────────────────────────────────────────────────────────┤                                                                             
 │ app/routers/auth.py    │ Add /refresh endpoint                                   │                                                                             
 └────────────────────────┴─────────────────────────────────────────────────────────┘                                                                             
 ---                                                                                                                                                              
 Verification                                                                                                                                                     
                                                                                                                                                                  
 # 1. Test embedding models filtered - should not see 'embed' models                                                                                              
 curl http://localhost:8080/api/models | jq '.models[].name'                                                                                                      
                                                                                                                                                                  
 # 2. Check no debug console.log in chat.js                                                                                                                       
 grep -n "console.log" static/js/chat.js                                                                                                                          
 # Should only show non-debug logs                                                                                                                                
                                                                                                                                                                  
 # 3. Test token refresh endpoint                                                                                                                                 
 curl -X POST http://localhost:8080/api/auth/refresh -v                                                                                                           
 # Should return 401 "No token provided" (expected without cookie)                                                                                                
                                                                                                                                                                  
 # 4. Manual UI test:                                                                                                                                             
 # - Login, wait 20+ minutes, verify still logged in (token refreshed)                                                                                            
 # - Try uploading multiple files to knowledge base simultaneously                                                                                                
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
                                                                                                                                                                  
 Requested permissions:                                                                                                                                           
   · Bash(prompt: run grep to verify changes)                                                                                                                     
                                                           
