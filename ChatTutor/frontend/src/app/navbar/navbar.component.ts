<<<<<<< HEAD
import { Component, Input, OnInit } from '@angular/core';
=======
import { Component, OnInit } from '@angular/core';
>>>>>>> origin/beta-main

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit{
  loggedin : boolean = false
<<<<<<< HEAD
  hidden : boolean = true
  @Input() ondashboard : boolean = false

=======
>>>>>>> origin/beta-main
  async ngOnInit(): Promise<void> {
    const respuser = await fetch('/isloggedin', {method: 'POST', headers: {'Content-Type': 'application/json'}})
    const user = await respuser.json()
    console.log(user['loggedin'])
    this.loggedin = user['loggedin']
<<<<<<< HEAD
    this.hidden = false
=======
>>>>>>> origin/beta-main
  }
}
