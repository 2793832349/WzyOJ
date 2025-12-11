eval 'git clone https://github.com/genuine-oj/deploy.git'
cd /root/deploy
eval 'docker --version'
eval 'apt update && apt install -y docker.io docker-compose'
eval 'systemctl start docker && systemctl enable docker'
eval 'docker --version && docker compose version'
eval 'docker-compose --version'
eval 'docker-compose -f docker-compose.builder.yml build'
eval 'docker-compose -f docker-compose.builder.yml run --rm build-frontend'
eval 'docker-compose build'
eval 'mkdir -p ./data/backend && touch ./data/backend/secret.key'
eval 'docker-compose up -d'
eval 'docker-compose ps'
eval 'docker-compose logs backend --tail=50'
eval 'docker logs oj-backend --tail 50'
eval 'curl -I http://localhost:80'
cd /root
eval 'git clone https://github.com/genuine-oj/backend.git'
eval 'git clone https://github.com/genuine-oj/frontend-naive.git'
eval 'git clone https://github.com/genuine-oj/judger.git'
eval 'chmod +x /root/start-dev.sh'
cd /root/deploy
eval 'docker exec -it oj-backend python3 manage.py shell'
eval "docker exec -it oj-backend bash -c \"cd /srv/server && python3 manage.py shell -c \\\"from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.filter(username='Wangzyy').first(); print('用户存在:', user is not None); print('用户名:', user.username if user else 'None'); print('是否为管理员:', user.is_superuser if user else 'None')\\\"\""
eval "docker exec -it oj-backend bash -c \"cd /srv/server && python3 manage.py shell -c \\\"from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='Wangzyy'); user.is_superuser = True; user.is_staff = True; user.save(); print('✓ 用户 Wangzyy 已设置为管理员'); print('  - is_superuser:', user.is_superuser); print('  - is_staff:', user.is_staff)\\\"\""
cd /root/frontend-naive
eval 'npm run build'
cd /root/deploy
eval 'chmod +x build-local-frontend.sh'
eval ./build-local-frontend.sh
eval 'docker-compose restart frontend'
eval 'docker-compose ps frontend'
eval 'grep -r "encodeURIComponent" /root/deploy/data/frontend/assets/ | head -5'
eval 'grep -o "file/\${encodeURIComponent" /root/deploy/data/frontend/assets/*.js | head -1'
eval 'cat /root/deploy/data/frontend/index.html'
eval 'grep -o "file/\${.*}.*delete" /root/deploy/data/frontend/assets/edit.40930e7d.js | head -1'
eval 'docker-compose restart frontend'
eval 'grep -A 2 -B 2 "removeFile.*file.*delete" /root/deploy/data/frontend/assets/edit.40930e7d.js | head -20'
eval 'grep -o "Ae\.delete\(\`/problem/\${[^}]*}/file/[^)]*" /root/deploy/data/frontend/assets/edit.40930e7d.js'
eval "grep -o 'Ae\\.delete.*problem.*file' /root/deploy/data/frontend/assets/edit.40930e7d.js | head -5"
eval "grep -o 'baseURL.*api' /root/deploy/data/frontend/assets/index.564f128e.js | head -3"
eval "echo \"当前部署的 edit.js 文件中的 removeFile 函数：\" && grep -o 'v=({file:m}).*Ae\\.delete[^,]*' /root/deploy/data/frontend/assets/edit.40930e7d.js | head -1"
eval 'docker exec oj-frontend cat /etc/nginx/conf.d/default.conf'
eval 'docker exec oj-frontend nginx -T 2>&1 | grep -A 20 "location /api"'
eval 'cat /root/deploy/data/frontend/index.html'
eval ./build-local-frontend.sh
eval 'ls -lh /root/deploy/data/frontend/assets/*.1765257808390.js | head -5'
eval "grep -o 'Ae\\.delete.*problem.*file' /root/deploy/data/frontend/assets/edit.0f202405.1765257808390.js | head -1"
eval 'cat /root/deploy/data/frontend/index.html'
eval 'docker-compose restart'
eval 'docker-compose ps'
eval "grep -o 'Ae\\.delete.*problem.*file.*encodeURIComponent' /root/deploy/data/frontend/assets/edit.0f202405.1765257808390.js | head -1"
eval "grep -o 'baseURL.*api' /root/deploy/data/frontend/assets/index.514d2de7.1765257808390.js | tail -1"
eval "grep -A 5 'Ik.create({baseURL' /root/deploy/data/frontend/assets/index.514d2de7.1765257808390.js | head -10"
eval "grep -o 'const [A-Z][a-z]*=.*delete' /root/deploy/data/frontend/assets/edit.0f202405.1765257808390.js | head -5"
eval "grep -o 'import.*Ae.*from' /root/deploy/data/frontend/assets/edit.0f202405.1765257808390.js | head -5"
eval ./build-local-frontend.sh
eval "grep -A 10 'removeFile.*file.*delete' /root/deploy/data/frontend/assets/edit.63535424.1765258651282.js | head -15"
eval "grep -o 'v=({file:m}).*return.*false' /root/deploy/data/frontend/assets/edit.63535424.1765258651282.js | head -1"
eval "grep 'encodeURIComponent.*name.*delete' /root/deploy/data/frontend/assets/edit.63535424.1765258651282.js | head -1"
eval "grep -o 'Ae\\.delete.*encodeURIComponent' /root/deploy/data/frontend/assets/edit.63535424.1765258651282.js | head -3"
eval "grep 'delete.*problem.*file' /root/deploy/data/frontend/assets/edit.63535424.1765258651282.js | head -1"
eval "grep -o 'Ae\\.delete[^,]*' /root/deploy/data/frontend/assets/edit.63535424.1765258651282.js | head -5"
eval 'ls -lh /root/deploy/data/frontend/assets/edit.*.1765258651282.js'
eval "grep 'removeFile' /root/deploy/data/frontend/assets/edit.*.1765258651282.js"
eval "grep '删除成功' /root/deploy/data/frontend/assets/edit.*.1765258651282.js"
eval "grep -l '题目标题' /root/deploy/data/frontend/assets/edit.*.1765258651282.js"
eval "grep -l 'u9898' /root/deploy/data/frontend/assets/edit.*.1765258651282.js"
eval "grep -o 'Ae\\.delete[^)]*' /root/deploy/data/frontend/assets/edit.367d27f6.1765258651282.js | head -3"
eval "cat /root/deploy/data/frontend/index.html | grep -o 'index\\.[^\"]*\\.js'"
eval ./build-local-frontend.sh
eval "grep 'show-remove-button' /root/deploy/data/frontend/assets/edit.*.1765259173739.js"
eval "grep -A 5 'b=m=>{Te.delete' /root/deploy/data/frontend/assets/edit.91f88d1a.1765259173739.js | head -10"
eval ./build-local-frontend.sh
eval './build-local-frontend.sh 2>&1 | tail -50'
eval './build-local-frontend.sh 2>&1 | tail -30'
eval './build-local-frontend.sh 2>&1 | tail -20'
eval 'docker logs oj-frontend --tail 50 2>&1 | grep DELETE'
eval 'docker exec oj-frontend cat /etc/nginx/conf.d/default.conf'
eval 'docker-compose restart frontend'
eval 'docker logs oj-frontend --tail 20 2>&1 | grep DELETE'
eval 'docker-compose restart backend'
eval 'docker logs oj-frontend --tail 5 2>&1 | grep DELETE'
eval 'docker exec oj-backend grep -A 2 "APPEND_SLASH" /srv/server/oj_backend/settings.py'
eval 'docker-compose build backend'
eval "docker exec oj-backend bash -c \"echo -e '\\n# Disable automatic slash appending to prevent 301 redirects\\nAPPEND_SLASH = False' >> /srv/server/oj_backend/settings.py\""
eval 'docker exec oj-backend grep "APPEND_SLASH" /srv/server/oj_backend/settings.py'
eval 'docker-compose restart backend'
eval 'docker logs oj-frontend --tail 10 2>&1 | grep DELETE'
eval 'docker-compose restart'
eval 'docker-compose ps'
eval './build-local-frontend.sh 2>&1 | tail -30'
cd /root/backend
eval 'cd /root/backend && python manage.py startapp oj_class'
eval 'mkdir -p oj_class/migrations && touch oj_class/__init__.py oj_class/models.py oj_class/views.py oj_class/serializers.py oj_class/urls.py oj_class/admin.py oj_class/apps.py oj_class/migrations/__init__.py'
cd /root/deploy
eval 'docker exec oj-backend python3 manage.py makemigrations oj_class'
eval 'docker exec oj-backend bash -c "cd /srv/server && python3 manage.py makemigrations oj_class"'
eval 'docker cp /root/backend/oj_class oj-backend:/srv/server/'
eval 'docker cp /root/backend/oj_backend/settings.py oj-backend:/srv/server/oj_backend/settings.py'
eval 'docker cp /root/backend/oj_backend/urls.py oj-backend:/srv/server/oj_backend/urls.py'
eval 'docker exec oj-backend bash -c "cd /srv/server && python3 manage.py makemigrations oj_class"'
eval 'docker exec oj-backend bash -c "cd /srv/server && python3 manage.py migrate oj_class"'
eval 'docker-compose restart backend'
cd /root/frontend-naive
eval 'mkdir -p /root/frontend-naive/src/pages/class'
cd /root/deploy
eval './build-local-frontend.sh 2>&1 | tail -30'
eval './build-local-frontend.sh 2>&1 | tail -20'
cd /root/frontend-naive
eval 'mv /root/frontend-naive/src/pages/class/_id.vue /root/frontend-naive/src/pages/class/_id.vue.backup && mv /root/frontend-naive/src/pages/class/_id_new.vue /root/frontend-naive/src/pages/class/_id.vue'
cd /root/deploy
eval './build-local-frontend.sh 2>&1 | tail -25'
eval './build-local-frontend.sh 2>&1 | tail -20'
eval './build-local-frontend.sh 2>&1 | tail -25'
eval 'docker cp /root/backend/oj_class/serializers.py oj-backend:/srv/server/oj_class/serializers.py'
eval 'docker-compose restart backend'
eval './build-local-frontend.sh 2>&1 | tail -25'
eval 'docker cp /root/backend/oj_class/views.py oj-backend:/srv/server/oj_class/views.py'
eval 'docker-compose restart backend'
eval './build-local-frontend.sh 2>&1 | tail -25'
eval 'docker cp /root/backend/oj_class/views.py oj-backend:/srv/server/oj_class/views.py && docker-compose restart backend'
eval './build-local-frontend.sh 2>&1 | tail -30'
eval './build-local-frontend.sh 2>&1 | tail -25'
eval 'docker cp /root/backend/oj_class/views.py oj-backend:/srv/server/oj_class/views.py && docker-compose restart backend'
cd /root/deploy
eval 'docker-compose -f docker-compose.builder.yml run --rm build-frontend'
eval 'docker-compose restart frontend'
eval 'docker-compose ps frontend'
eval 'docker-compose -f docker-compose.builder.yml run --rm build-frontend'
eval 'docker-compose restart frontend'
eval 'docker-compose ps frontend'
cd /root/frontend-naive
eval 'grep -r "班级" dist/assets/*.js | head -5'
cd /root/deploy
eval 'docker exec oj-frontend ls -la /usr/share/nginx/html/assets/ | head -10'
eval "docker exec oj-frontend sh -c \"grep -l '班级' /usr/share/nginx/html/assets/*.js\""
cd /root/frontend-naive
eval 'yarn build'
cd /root
eval 'which npm'
cd /root/deploy
eval 'docker-compose -f docker-compose.builder.yml run --rm build-frontend'
eval "docker exec oj-frontend sh -c \"grep -l '班级' /usr/share/nginx/html/assets/*.js | head -3\""
eval 'docker-compose restart frontend'
eval "docker exec oj-frontend sh -c \"grep '班级' /usr/share/nginx/html/assets/*.js\" | head -3"
eval 'docker-compose -f docker-compose.builder.yml run --rm build-frontend 2>&1 | grep -E "(Using|frontend)"'
eval 'docker-compose -f docker-compose.builder.yml run --rm build-frontend bash -c "echo USE_LOCAL_SOURCE=$USE_LOCAL_SOURCE"'
eval 'docker-compose -f docker-compose.builder.yml run --rm build-frontend ls -la /root/ | grep frontend'
cd /root
eval 'docker run --rm -v /root/frontend-naive:/app -w /app node:18 bash -c "yarn install --registry=https://registry.npmmirror.com && yarn build"'
eval 'rm -rf /root/deploy/data/frontend/* && cp -r /root/frontend-naive/dist/* /root/deploy/data/frontend/'
cd /root/deploy
eval 'docker-compose restart frontend'
cd /root
eval 'grep -r "班级" /root/deploy/data/frontend/assets/*.js 2>/dev/null | head -1'
eval 'grep "班级" /root/frontend-naive/src/AppHeader.vue'
eval 'cat /root/deploy/data/frontend/index.html'
eval 'ls -la /root/deploy/data/frontend/assets/index.*.js'
eval 'grep "班级" /root/deploy/data/frontend/assets/index.6975508a.1765368327361.js | head -1'
eval 'grep "TeamOutlined" /root/deploy/data/frontend/assets/*.js | head -1'
eval "node -e \"const fs = require('fs'); const content = fs.readFileSync('/root/deploy/data/frontend/assets/index.6975508a.1765368327361.js', 'utf8'); console.log(content.includes('班级') ? '找到班级' : '未找到班级'); console.log(content.includes('class_list') ? '找到class_list路由' : '未找到class_list路由'); console.log(content.includes('TeamOutlined') ? '找到TeamOutlined' : '未找到TeamOutlined');\""
eval "python3 -c \"with open('/root/deploy/data/frontend/assets/index.6975508a.1765368327361.js', 'r', encoding='utf-8') as f: content = f.read(); print('找到班级' if '班级' in content else '未找到班级'); print('找到class_list' if 'class_list' in content else '未找到class_list'); print('找到TeamOutlined' if 'TeamOutlined' in content else '未找到TeamOutlined')\""
eval "python3 -c \"import re; content = open('/root/deploy/data/frontend/assets/index.6975508a.1765368327361.js', 'r', encoding='utf-8').read(); matches = re.findall(r'TeamOutlined.{0,200}', content); print(matches[0] if matches else 'Not found')\""
eval "python3 << 'EOF'
content = open('/root/deploy/data/frontend/assets/index.6975508a.1765368327361.js', 'r', encoding='utf-8').read()
# 搜索 class_list 附近的内容
import re
matches = re.findall(r'.{100}class_list.{100}', content)
for i, match in enumerate(matches[:3]):
    print(f\"Match {i+1}:\")
    print(match)
    print(\"---\")
EOF"
eval "python3 -c \"print('\\\\u8BBE\\\\u7F6E')\""
eval 'ps aux | grep python | grep -v grep'
eval 'docker logs oj-backend --tail 50'
eval 'docker exec oj-backend tail -100 /var/log/uwsgi.log'
eval 'docker exec oj-backend tail -200 /var/log/uwsgi.log | grep -A 20 "PUT /api/class/assignment/1/"'
eval 'docker exec oj-backend cat /var/log/django.log | tail -100'
eval 'docker restart oj-backend'
cd /root/backend
eval "docker exec oj-backend python manage.py shell -c \"from oj_class.models import Assignment, AssignmentProblem; ap = AssignmentProblem.objects.filter(assignment_id=1).first(); print(f'AssignmentProblem: {ap}'); print(f'Problem: {ap.problem if ap else None}'); print(f'Reference Problem ID: {ap.problem.reference_problem_id if ap and ap.problem else None}')\""
cd /root
eval "docker exec -w /srv/server oj-backend python manage.py shell -c \"from oj_class.models import Assignment, AssignmentProblem; ap = AssignmentProblem.objects.filter(assignment_id=1).first(); print(f'AssignmentProblem: {ap}'); print(f'Problem: {ap.problem if ap else None}'); print(f'Reference Problem ID: {ap.problem.reference_problem_id if ap and ap.problem else None}')\""
eval 'docker exec -w /srv/server oj-backend python manage.py shell -c "from oj_class.models import Assignment; print(Assignment.objects.all())"'
eval 'docker restart oj-backend'
eval 'docker logs backend 2>&1 | tail -50'
eval 'docker ps -a'
eval 'docker logs oj-backend 2>&1 | tail -100'
eval 'docker exec oj-backend cat /tmp/uwsgi.log 2>&1 | tail -100'
eval 'docker exec oj-backend find /srv -name "*.log" -type f 2>/dev/null | head -20'
eval "docker exec oj-backend python manage.py shell -c \"from oj_class.models import ClassProblem; cp = ClassProblem.objects.filter(is_reference=True).first(); print(f'ID: {cp.id}, is_reference: {cp.is_reference}, reference_problem: {cp.reference_problem}')\" 2>&1"
eval 'docker exec oj-backend ls -la /srv/server/'
eval "docker exec -w /srv/server oj-backend python manage.py shell -c \"from oj_class.models import ClassProblem; cp = ClassProblem.objects.filter(is_reference=True).first(); print(f'ID: {cp.id if cp else None}, is_reference: {cp.is_reference if cp else None}, reference_problem: {cp.reference_problem if cp else None}')\" 2>&1"
eval "docker exec -w /srv/server oj-backend python manage.py shell -c \"from oj_class.models import ClassProblem; problematic = ClassProblem.objects.filter(is_reference=True, reference_problem__isnull=True); print(f'Count: {problematic.count()}'); [print(f'ID: {p.id}, title: {p.title}') for p in problematic]\" 2>&1"
eval "docker exec -w /srv/server oj-backend python manage.py shell << 'EOF'
from oj_class.models import Assignment, AssignmentProblem
from oj_submission.models import Submission

assignment = Assignment.objects.get(id=1)
class_obj = assignment.class_obj

print(f\"Assignment: {assignment.title}\")
print(f\"Class: {class_obj.title}\")
print(f\"Teacher: {class_obj.teacher}\")

# Get students
students = class_obj.members.filter(role='student').select_related('user')
print(f\"Students count: {students.count()}\")

# Get assignment problems
assignment_problems = AssignmentProblem.objects.filter(
    assignment=assignment
).select_related('problem', 'problem__reference_problem').order_by('order')
print(f\"Assignment problems count: {assignment_problems.count()}\")

for ap in assignment_problems:
    print(f\"\\nProblem: {ap.problem}\")
    print(f\"  is_reference: {ap.problem.is_reference}\")
    print(f\"  reference_problem: {ap.problem.reference_problem}\")
    try:
        title = ap.problem.get_title()
        print(f\"  title: {title}\")
    except Exception as e:
        print(f\"  ERROR getting title: {e}\")
        import traceback
        traceback.print_exc()
EOF
"
eval "docker exec -w /srv/server oj-backend python -c \"
from oj_class.models import Assignment, AssignmentProblem
from oj_submission.models import Submission

assignment = Assignment.objects.get(id=1)
class_obj = assignment.class_obj

print(f'Assignment: {assignment.title}')
print(f'Class: {class_obj.title}')
print(f'Teacher: {class_obj.teacher}')

# Get students
students = class_obj.members.filter(role='student').select_related('user')
print(f'Students count: {students.count()}')

# Get assignment problems
assignment_problems = AssignmentProblem.objects.filter(
    assignment=assignment
).select_related('problem', 'problem__reference_problem').order_by('order')
print(f'Assignment problems count: {assignment_problems.count()}')

for ap in assignment_problems:
    print(f'Problem: {ap.problem}')
    print(f'  is_reference: {ap.problem.is_reference}')
    print(f'  reference_problem: {ap.problem.reference_problem}')
    try:
        title = ap.problem.get_title()
        print(f'  title: {title}')
    except Exception as e:
        print(f'  ERROR getting title: {e}')
        import traceback
        traceback.print_exc()
\" 2>&1"
eval 'docker exec oj-backend supervisorctl tail uwsgi stderr | tail -100'
eval 'docker exec oj-backend supervisorctl tail uwsgi stdout | tail -200'
eval 'docker exec oj-backend supervisorctl restart uwsgi'
eval 'docker exec oj-backend tail -f /tmp/supervisor.log 2>&1 &
sleep 1
echo "Logs are being monitored..."
'
eval 'curl -s -X GET "http://localhost/api/class/assignment/1/grades/" -H "Cookie: sessionid=YOUR_SESSION" 2>&1 | head -50'
eval 'docker exec oj-backend find /var/log -name "*.log" -type f 2>/dev/null | head -20'
eval 'docker exec oj-backend tail -100 /var/log/uwsgi.log 2>&1 | grep -A 20 "grades"'
eval 'docker exec oj-backend grep -A 30 "Error in get_grades" /var/log/uwsgi.log 2>&1 | tail -50'
eval 'docker exec oj-backend grep -A 5 "def get_grades" /srv/server/oj_class/views.py | head -10'
cd /root/deploy
eval 'docker-compose build backend'
eval 'docker-compose up -d backend'
eval 'docker stop oj-backend && docker rm oj-backend'
eval 'docker ps -a | grep backend'
eval 'docker rm 59bef73685e7_oj-backend'
eval 'docker-compose up -d backend'
cd /root
eval 'docker exec oj-backend grep -A 10 "def get_grades" /srv/server/oj_class/views.py | head -15'
eval 'sleep 10 && docker logs oj-backend 2>&1 | tail -20'
eval 'docker exec oj-backend tail -f /var/log/uwsgi.log 2>&1 &
TAIL_PID=$!
sleep 2
echo "Monitoring logs... Please try accessing the grades page now."
sleep 15
kill $TAIL_PID 2>/dev/null
'
eval 'docker exec oj-backend tail -50 /var/log/uwsgi.log 2>&1 | grep -E "(grades|Error|error)" | tail -20'
cd /root/deploy
eval 'docker-compose build backend'
cd /root/frontend-naive
eval 'npm run build'
eval 'which pnpm'
cd /root
eval 'ls -la /root/deploy/data/frontend/ | head -20'
eval 'cp -r /root/frontend-naive/dist/* /root/deploy/data/frontend/'
cd /root/deploy
eval 'docker-compose restart backend'
cd /root
eval 'sleep 8 && docker logs oj-backend 2>&1 | tail -10'
eval 'cp -r /root/frontend-naive/dist/* /root/deploy/data/frontend/'
cd /root/deploy
eval 'docker-compose restart frontend'
cd /root
eval 'docker ps | grep frontend'
cd /root/frontend-naive
eval 'which node'
cd /root/deploy
eval 'chmod +x build-local-frontend.sh && ./build-local-frontend.sh'
cd /root
eval 'docker ps | grep frontend'
eval 'grep -r "Wangzyy" /root/deploy/data/frontend/assets/*.js 2>/dev/null | head -1'
eval 'docker exec oj-backend tail -50 /var/log/uwsgi.log 2>&1 | grep -A 5 "grades"'
eval "curl -s http://localhost/api/class/assignment/1/grades/ -H \"Cookie: sessionid=\$(docker exec oj-backend cat /tmp/test_session 2>/dev/null || echo '')\" 2>&1 | python3 -m json.tool 2>/dev/null | head -50"
eval 'ls -lh /root/deploy/data/frontend/assets/*.js | head -5'
eval 'grep -l "rank" /root/deploy/data/frontend/assets/*1765381703238.js | head -3'
eval 'cd /root/deploy/data/frontend/assets && rm -f *1765368327361.js *1765368327361.css && ls -lh | wc -l'
cd /root
eval 'cat /root/deploy/data/frontend/index.html | grep -E "\.js|\.css" | head -10'
cd /root/deploy
eval 'docker-compose restart frontend'
cd /root
eval 'grep -o "title:\"序号\"[^}]*" /root/deploy/data/frontend/assets/_id.*.js 2>/dev/null | head -1'
eval 'docker exec oj-backend grep -A 3 "添加排名序号" /srv/server/oj_class/views.py'
cd /root/deploy
eval 'docker-compose build backend'
eval 'docker-compose build --no-cache backend'
eval 'docker-compose restart backend'
cd /root
eval 'sleep 10 && docker exec oj-backend grep -A 3 "添加排名序号" /srv/server/oj_class/views.py'
eval 'docker exec oj-backend cat /srv/server/oj_class/views.py | grep -A 10 "grades_data.append"'
eval 'ls -la /root/backend/oj_class/views.py'
eval 'docker cp /root/backend/oj_class/views.py oj-backend:/srv/server/oj_class/views.py'
eval 'docker exec oj-backend supervisorctl restart uwsgi'
eval 'sleep 5 && docker exec oj-backend grep -A 3 "添加排名序号" /srv/server/oj_class/views.py'
cd /root/deploy
eval 'cd /root/deploy && ./build-local-frontend.sh'
eval 'docker rmi genuine-oj/frontend-builder-local 2>/dev/null; cd /root/deploy && ./build-local-frontend.sh'
eval 'docker exec oj-backend tail -50 /var/log/uwsgi.log'
eval 'docker exec oj-backend cat /srv/server/logs/django.log 2>/dev/null || docker exec oj-backend tail -100 /var/log/supervisor/uwsgi-stderr*.log 2>/dev/null || echo "No error logs found"'
eval 'docker exec -w /srv/server oj-backend python manage.py shell'
eval "docker exec oj-backend curl -X PUT http://localhost:8080/api/class/assignment/1/ -H \"Content-Type: application/json\" -H \"Authorization: Bearer test\" -d '{\"title\":\"测试\",\"problem_ids\":[1]}' -v 2>&1 | tail -50"
eval 'docker exec oj-backend supervisorctl status'
eval "docker exec -w /srv/server oj-backend python -c \"
from oj_class.models import Assignment, ClassProblem
from oj_problem.models import Problem

# 获取作业1
assignment = Assignment.objects.get(id=1)
print(f'Assignment: {assignment}')
print(f'Class: {assignment.class_obj}')

# 检查问题1是否存在
problem = Problem.objects.filter(id=1).first()
print(f'Problem 1 exists: {problem}')

# 尝试获取或创建 ClassProblem
if problem:
    cp, created = ClassProblem.objects.get_or_create(
        class_obj=assignment.class_obj,
        reference_problem_id=1,
        defaults={'is_reference': True, 'order': 0}
    )
    print(f'ClassProblem: {cp}, created: {created}')
\""
eval "docker exec -w /srv/server oj-backend python manage.py shell -c \"
from oj_class.models import Assignment, ClassProblem
from oj_problem.models import Problem

# 获取作业1
assignment = Assignment.objects.get(id=1)
print(f'Assignment: {assignment}')
print(f'Class: {assignment.class_obj}')

# 检查问题1是否存在
problem = Problem.objects.filter(id=1).first()
print(f'Problem 1 exists: {problem}')

# 尝试获取或创建 ClassProblem
if problem:
    cp, created = ClassProblem.objects.get_or_create(
        class_obj=assignment.class_obj,
        reference_problem_id=1,
        defaults={'is_reference': True, 'order': 0}
    )
    print(f'ClassProblem: {cp}, created: {created}')
\""
eval "docker exec -w /srv/server oj-backend python -c \"import django; django.setup(); from oj_class.views import AssignmentViewSet; print('Import successful')\""
eval 'docker exec oj-backend python -m py_compile /srv/server/oj_class/views.py'
eval 'docker exec oj-backend python -m py_compile /srv/server/oj_class/serializers.py'
eval 'docker exec oj-backend env | grep MODE'
eval 'docker exec oj-backend cat /srv/uwsgi.ini'
eval "docker exec -w /srv/server oj-backend python manage.py shell -c \"
from django.test import RequestFactory
from oj_class.views import AssignmentViewSet
from oj_user.models import User
from oj_class.models import Assignment
import json

# 创建请求
factory = RequestFactory()
user = User.objects.filter(is_staff=True).first()
print(f'User: {user}')

# 模拟 PUT 请求
data = {
    'title': '测试作业',
    'description': '测试描述',
    'class_obj': 1,
    'problem_ids': [1]
}

request = factory.put(
    '/api/class/assignment/1/',
    data=json.dumps(data),
    content_type='application/json'
)
request.user = user

# 执行更新
try:
    view = AssignmentViewSet.as_view({'put': 'update'})
    response = view(request, pk=1)
    print(f'Response status: {response.status_code}')
    print(f'Response data: {response.data if hasattr(response, \\\"data\\\") else response.content}')
except Exception as e:
    import traceback
    print(f'Error: {e}')
    traceback.print_exc()
\""
eval 'docker exec oj-backend cat /srv/server/oj_class/serializers.py | tail -30'
eval 'docker inspect oj-backend | grep -A 10 "Mounts"'
eval 'docker inspect oj-backend | grep -B 2 -A 2 "/srv/server"'
eval 'docker cp /root/backend/oj_class/serializers.py oj-backend:/srv/server/oj_class/serializers.py'
eval 'docker cp /root/backend/oj_class/views.py oj-backend:/srv/server/oj_class/views.py'
eval 'docker exec oj-backend supervisorctl restart uwsgi'
eval "docker exec -w /srv/server oj-backend python manage.py shell -c \"
from django.test import RequestFactory
from oj_class.views import AssignmentViewSet
from oj_user.models import User
import json

factory = RequestFactory()
user = User.objects.filter(is_staff=True).first()

data = {
    'title': '测试作业-更新',
    'description': '测试描述',
    'class_obj': 1,
    'problem_ids': [1]
}

request = factory.put(
    '/api/class/assignment/1/',
    data=json.dumps(data),
    content_type='application/json'
)
request.user = user

try:
    view = AssignmentViewSet.as_view({'put': 'update'})
    response = view(request, pk=1)
    print(f'Success\! Status: {response.status_code}')
    if hasattr(response, 'data'):
        print(f'Title: {response.data.get(\\\"title\\\")}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
\""
