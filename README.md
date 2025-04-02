# InfiniteCampusAPI
 
Example:

```python
from infinitecampusapi import InfiniteCampus

test = InfiniteCampus(
    token_url="https://iacloud2.infinitecampus.org/campus/oauth2/token?appName=example",
    base_url="https://iacloud2.infinitecampus.org/campus/api/oneroster/v1p2/example/ims/oneroster/rostering/v1p2/",
    secret="api_secret",
    key="api_key",
)
print(test.students.get_students())
print(test.student.get_student("12345678-1234-1234-1234-1234567890ab"))
print(test.teachers.get_teachers())
print(test.teachers.get_teacher("12345678-1234-1234-1234-1234567890ab"))
print(test.schools.get_schools())
print(test.schools.get_school("12345678-1234-1234-1234-1234567890ab"))
print(test.schools.get_school_students("12345678-1234-1234-1234-123456789ab"))
print(test.demographics.get_demographics())
print(test.demographics.get_demographic("12345678-1234-1234-1234-1234567890ab"))
print(test.student.get_student_demographics(test.students.get_students()[0]))
print(test.academicSessions.get_academic_sessions())
print(test.academicSessions.get_academic_session("12345678-1234-1234-1234-1234567890ab"))
```