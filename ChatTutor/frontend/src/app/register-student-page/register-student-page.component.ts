import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-register-student-page',
  templateUrl: './register-student-page.component.html',
  styleUrls: ['./register-student-page.component.css']
})
export class RegisterStudentPageComponent {
  @Input() endpoint: String = "/student/register"
}
