const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('vct', {
  apiBase: 'http://127.0.0.1:8000',
  uiBase: 'http://127.0.0.1:3000'
});
