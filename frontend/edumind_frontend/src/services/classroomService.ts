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
  UpdateLessonBlockRequest,
  UpdateLessonRequest,
  UpdateLessonSectionRequest,
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

export async function deleteProfessorClassroom(
  classroomId: number,
  token: string,
): Promise<void> {
  return requestJson<void>(
    API_ENDPOINTS.classrooms.professorDetail(classroomId),
    { method: 'DELETE', token },
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

export async function updateLesson(
  classroomId: number,
  lessonId: number,
  payload: UpdateLessonRequest,
  token: string,
): Promise<Lesson> {
  return requestJson<Lesson>(
    API_ENDPOINTS.classrooms.professorLessonDetail(classroomId, lessonId),
    { method: 'PATCH', body: payload, token },
  )
}

export async function deleteLesson(
  classroomId: number,
  lessonId: number,
  token: string,
): Promise<void> {
  return requestJson<void>(
    API_ENDPOINTS.classrooms.professorLessonDetail(classroomId, lessonId),
    { method: 'DELETE', token },
  )
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

export async function updateLessonSection(
  classroomId: number,
  lessonId: number,
  sectionId: number,
  payload: UpdateLessonSectionRequest,
  token: string,
): Promise<LessonSection> {
  return requestJson<LessonSection>(
    API_ENDPOINTS.classrooms.professorSectionDetail(classroomId, lessonId, sectionId),
    { method: 'PATCH', body: payload, token },
  )
}

export async function deleteLessonSection(
  classroomId: number,
  lessonId: number,
  sectionId: number,
  token: string,
): Promise<void> {
  return requestJson<void>(
    API_ENDPOINTS.classrooms.professorSectionDetail(classroomId, lessonId, sectionId),
    { method: 'DELETE', token },
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

// Usa multipart apenas quando há arquivo; o navegador define o Content-Type com o boundary.
function buildLessonBlockBody(
  payload: CreateLessonBlockRequest | UpdateLessonBlockRequest,
): CreateLessonBlockRequest | UpdateLessonBlockRequest | FormData {
  const hasFile =
    payload.arquivo_imagem instanceof File || payload.arquivo_video instanceof File

  if (!hasFile) {
    const { arquivo_imagem: _imagem, arquivo_video: _video, ...jsonPayload } = payload
    return jsonPayload
  }

  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value == null) {
      return
    }
    if (value instanceof File) {
      formData.append(key, value)
    } else if (typeof value === 'object') {
      formData.append(key, JSON.stringify(value))
    } else {
      formData.append(key, String(value))
    }
  })
  return formData
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
    { method: 'POST', body: buildLessonBlockBody(payload), token },
  )
}

export async function updateLessonBlock(
  classroomId: number,
  lessonId: number,
  sectionId: number,
  blockId: number,
  payload: UpdateLessonBlockRequest,
  token: string,
): Promise<LessonBlock> {
  return requestJson<LessonBlock>(
    API_ENDPOINTS.classrooms.professorBlockDetail(classroomId, lessonId, sectionId, blockId),
    { method: 'PATCH', body: buildLessonBlockBody(payload), token },
  )
}

export async function deleteLessonBlock(
  classroomId: number,
  lessonId: number,
  sectionId: number,
  blockId: number,
  token: string,
): Promise<void> {
  return requestJson<void>(
    API_ENDPOINTS.classrooms.professorBlockDetail(classroomId, lessonId, sectionId, blockId),
    { method: 'DELETE', token },
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