import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit{
  loggedin : boolean = false
  async ngOnInit(): Promise<void> {
    const respuser = await fetch('/isloggedin', {method: 'POST', headers: {'Content-Type': 'application/json'}})
    const user = await respuser.json()
    console.log(user['loggedin'])
    this.loggedin = user['loggedin']
  }
}
