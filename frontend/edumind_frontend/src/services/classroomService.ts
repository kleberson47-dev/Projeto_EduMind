import type {
  Activity,
  Classroom,
  ClassroomDetail,
  CreateActivityRequest,
  CreateClassroomRequest,
  CreateGradeRequest,
  CreateLessonBlockRequest,
  CreateLessonRequest,
  CreateLessonSectionRequest,
  Grade,
  JoinClassroomRequest,
  JoinClassroomResponse,
  Lesson,
  LessonBlock,
  LessonSection,
  UpdateClassroomRequest,
  UpdateClassroomResponse,
} from '../models/Classroom'
import { API_ENDPOINTS } from '../utils/api'
import { requestJson } from '../utils/requests'

export async function getProfessorClassrooms(token: string): Promise<Classroom[]> {
  return requestJson<Classroom[]>(API_ENDPOINTS.classrooms.listCreate, {
    method: 'GET',
    token,
  })
}

export async function createClassroom(
  payload: CreateClassroomRequest,
  token: string,
): Promise<ClassroomDetail> {
  return requestJson<ClassroomDetail>(API_ENDPOINTS.classrooms.listCreate, {
    method: 'POST',
    body: payload,
    token,
  })
}

export async function getStudentClassrooms(token: string): Promise<Classroom[]> {
  return requestJson<Classroom[]>(API_ENDPOINTS.classrooms.studentList, {
    method: 'GET',
    token,
  })
}

export async function joinClassroom(
  payload: JoinClassroomRequest,
  token: string,
): Promise<JoinClassroomResponse> {
  return requestJson<JoinClassroomResponse>(API_ENDPOINTS.classrooms.join, {
    method: 'POST',
    body: payload,
    token,
  })
}

export async function getStudentClassroomDetail(
  classroomId: number,
  token: string,
): Promise<ClassroomDetail> {
  return requestJson<ClassroomDetail>(
    API_ENDPOINTS.classrooms.studentDetail(classroomId),
    { method: 'GET', token },
  )
}

export async function getProfessorClassroomDetail(
  classroomId: number,
  token: string,
): Promise<ClassroomDetail> {
  return requestJson<ClassroomDetail>(
    API_ENDPOINTS.classrooms.professorDetail(classroomId),
    { method: 'GET', token },
  )
}

export async function updateProfessorClassroom(
  classroomId: number,
  payload: UpdateClassroomRequest,
  token: string,
): Promise<UpdateClassroomResponse> {
  return requestJson<UpdateClassroomResponse>(
    API_ENDPOINTS.classrooms.professorDetail(classroomId),
    { method: 'PATCH', body: payload, token },
  )
}

export async function getProfessorActivities(
  classroomId: number,
  token: string,
): Promise<Activity[]> {
  return requestJson<Activity[]>(API_ENDPOINTS.classrooms.professorActivities(classroomId), {
    method: 'GET',
    token,
  })
}

export async function createActivity(
  classroomId: number,
  payload: CreateActivityRequest,
  token: string,
): Promise<Activity> {
  return requestJson<Activity>(API_ENDPOINTS.classrooms.professorActivities(classroomId), {
    method: 'POST',
    body: payload,
    token,
  })
}

export async function getStudentActivities(
  classroomId: number,
  token: string,
): Promise<Activity[]> {
  return requestJson<Activity[]>(API_ENDPOINTS.classrooms.studentActivities(classroomId), {
    method: 'GET',
    token,
  })
}

export async function getProfessorGrades(
  classroomId: number,
  token: string,
): Promise<Grade[]> {
  return requestJson<Grade[]>(API_ENDPOINTS.classrooms.professorGrades(classroomId), {
    method: 'GET',
    token,
  })
}

export async function createGrade(
  classroomId: number,
  payload: CreateGradeRequest,
  token: string,
): Promise<Grade> {
  return requestJson<Grade>(API_ENDPOINTS.classrooms.professorGrades(classroomId), {
    method: 'POST',
    body: payload,
    token,
  })
}

export async function getStudentGrades(
  classroomId: number,
  token: string,
): Promise<Grade[]> {
  return requestJson<Grade[]>(API_ENDPOINTS.classrooms.studentGrades(classroomId), {
    method: 'GET',
    token,
  })
}

export async function getProfessorLessons(
  classroomId: number,
  token: string,
): Promise<Lesson[]> {
  return requestJson<Lesson[]>(API_ENDPOINTS.classrooms.professorLessons(classroomId), {
    method: 'GET',
    token,
  })
}

export async function createLesson(
  classroomId: number,
  payload: CreateLessonRequest,
  token: string,
): Promise<Lesson> {
  return requestJson<Lesson>(API_ENDPOINTS.classrooms.professorLessons(classroomId), {
    method: 'POST',
    body: payload,
    token,
  })
}

export async function getStudentLessons(
  classroomId: number,
  token: string,
): Promise<Lesson[]> {
  return requestJson<Lesson[]>(API_ENDPOINTS.classrooms.studentLessons(classroomId), {
    method: 'GET',
    token,
  })
}

export async function getStudentLessonDetail(
  classroomId: number,
  lessonId: number,
  token: string,
): Promise<Lesson> {
  return requestJson<Lesson>(
    API_ENDPOINTS.classrooms.studentLessonDetail(classroomId, lessonId),
    { method: 'GET', token },
  )
}

export async function getProfessorLessonSections(
  classroomId: number,
  lessonId: number,
  token: string,
): Promise<LessonSection[]> {
  return requestJson<LessonSection[]>(
    API_ENDPOINTS.classrooms.professorSections(classroomId, lessonId),
    { method: 'GET', token },
  )
}

export async function createLessonSection(
  classroomId: number,
  lessonId: number,
  payload: CreateLessonSectionRequest,
  token: string,
): Promise<LessonSection> {
  return requestJson<LessonSection>(
    API_ENDPOINTS.classrooms.professorSections(classroomId, lessonId),
    { method: 'POST', body: payload, token },
  )
}

export async function getStudentLessonSections(
  classroomId: number,
  lessonId: number,
  token: string,
): Promise<LessonSection[]> {
  return requestJson<LessonSection[]>(
    API_ENDPOINTS.classrooms.studentSections(classroomId, lessonId),
    { method: 'GET', token },
  )
}

export async function getProfessorLessonBlocks(
  classroomId: number,
  lessonId: number,
  sectionId: number,
  token: string,
): Promise<LessonBlock[]> {
  return requestJson<LessonBlock[]>(
    API_ENDPOINTS.classrooms.professorBlocks(classroomId, lessonId, sectionId),
    { method: 'GET', token },
  )
}

export async function createLessonBlock(
  classroomId: number,
  lessonId: number,
  sectionId: number,
  payload: CreateLessonBlockRequest,
  token: string,
): Promise<LessonBlock> {
  return requestJson<LessonBlock>(
    API_ENDPOINTS.classrooms.professorBlocks(classroomId, lessonId, sectionId),
    { method: 'POST', body: payload, token },
  )
}

export async function getStudentLessonBlocks(
  classroomId: number,
  lessonId: number,
  sectionId: number,
  token: string,
): Promise<LessonBlock[]> {
  return requestJson<LessonBlock[]>(
    API_ENDPOINTS.classrooms.studentBlocks(classroomId, lessonId, sectionId),
    { method: 'GET', token },
  )
}