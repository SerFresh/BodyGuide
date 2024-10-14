module.exports = { 
  apps: [ 
    { 
      name: "BodyGuide",  // ชื่อแอปพลิเคชัน 
      script: "gunicorn", 
      args: "project.wsgi:application --bind 0.0.0.0:8000",  // ใช้ Gunicorn เพื่อรันแอปพลิเคชัน Django 
      interpreter: "python3", 
      watch: false, 
      env: { 
        "DJANGO_SETTINGS_MODULE": "project.settings", 
        "PYTHONUNBUFFERED": "1" 
      } 
    } 
  ] 
}; 
