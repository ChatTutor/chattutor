import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class DataProviderService {

  constructor(private http: HttpClient) { }

  /**
   * Generate random string from given chars
   * @param length 
   * @param chars 
   * @returns 
   */
  randomString(length : number, chars : any) {
      var result = '';
      for (var i = length; i > 0; --i) result += chars[Math.floor(Math.random() * chars.length)];
      return result;
  }

  /**
   * Generate random string from a-z
   * @param length 
   * @returns 
   */
  randomAlphaString(length : number) {
    return this.randomString(length, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
  }

  /**
   * Generate random string from a-z 0-9
   * @param length 
   * @returns 
   */
  randomAlphaNumString(length : number) {
    return this.randomString(length, '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
  }

  /**
   * Return logged in user if loggedin
   * @returns User
   */
  async getLoggedInUser():  Promise<any> {
    const resp = await fetch('/getuser', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    return await resp.json();
  }

  /**
   * 
   * @returns {"isloggedin" : true/false} true if session is authed, false otherwise
   */
  async isAuthd():  Promise<any> {
    const resp = await fetch('/isloggedin', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    return await resp.json();
  }

  /**
   * Get course sections
   * @param email owner user email
   * @param course_id course_id of the course
   * @returns the user sections
   */
  async getUserCourseSections(email : string, course_id : any):  Promise<any>  {
    const resp = await fetch(`/users/${email}/courses/${course_id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return await resp.json();
  }

  /**
   * Get courses of user
   * @param email email of user
   * @returns 
   */
  async getUserCourses(email: string):  Promise<any> {
    const resp = await fetch(`/users/${email}/mycourses`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    return await resp.json()
  }

  /**
   * Delecte a doc from a section
   * @param doc doc (section) to delete
   * @param collection collection to delete from
   * @returns response
   */
  async deleteDoc_Unsafe(doc : any, collection : any):  Promise<any> {
    let data = JSON.stringify({
        collection: collection,
        doc: doc
    })
    let response = await fetch('/delete_doc', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
    return await response.json()
  }

  /**
   * Create collection using webpages specified by the list of urls as sections
   * @param urls array of strings specifying urls to parse
   * @param coursename collection name
   * @param prof prof name
   * @returns 
   */
  async addUrlsToKnowledgeBase(urls : string[], coursename : string, prof : string) {
    let data = JSON.stringify({url_to_parse: urls, collection_name: coursename, course_name: coursename, coursename: coursename, proffessor: prof})
    let response = await fetch('/prep/course/parse', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
    return await response.json()
  }

  async sendCollection(url : string, coursename : string, prof : string, component_state : any) {
    let data = JSON.stringify({url_to_parse: url, collection_name: coursename, course_name: coursename, coursename: coursename, proffessor: prof, manual: true})
    let response = await fetch('/prep/course/register', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
    return await response.json();
  }

  /**
   * 
   * @param url Origin URL of the web-graph to parse
   * @param coursename Name of the course
   * @param prof Prof. teaching the course if applicable
   * @param component_state Component to modify on completion:
   * 
   * **component_state : dict** -- Should have the following mutable params:
   *      - is_ready (bool): toggles when parsing is done
   *      - url_collection_name (string): is set to the generated collection name
   *                                      once the parsing is done
   *      - parsed_sections (dict[]): parsed sections in a dict form
   *      - parsed_urls_array (string[]): parsed sectoins' urls ([s.section_url for s in parsed_sections])
   */
  async scrapeOriginURLNode(url : string, coursename : string, prof : string, component_state : any) {
    let data = JSON.stringify({url_to_parse: url, collection_name: coursename, course_name: coursename, coursename: coursename, proffessor: prof})
    let response = await fetch('/prep/course/register', {method: 'POST', headers:{'Content-Type':'application/json'}, body: data})
    const reader = response.body!.getReader()
    let fulldata = ''
    let added_sections : any = {}
    let course_chroma_col = ''

    async function read(element: any): Promise<void> {
      let par = await reader.read()
      if(par.done) {
          element.is_ready = true
          element.url_collection_name = course_chroma_col
          return;
      }
      const string_value = new TextDecoder().decode(par.value)
      fulldata += ('\n\n' + string_value)
      const data:any[] = fulldata.split('\n\n')
          .filter(Boolean)
          .map(chunk => {
              let spl = null
              try {
                  spl = JSON.parse(chunk.split('data: ')[1]) }
              catch (e) { spl = {}
              }
              return spl
          })

      console.log("DATA: ", data)
      console.log("FULL DATA: ", fulldata)
      console.log("SVA: ", string_value)

      data.forEach(sectionarr => {
        sectionarr.forEach((section: any) => {
            if (added_sections[section['section_id']] != 1) {
              element.parsed_urls_array.push(section['section_url'])
              element.parsed_sections.push(section)
              added_sections[section['section_id']] = 1
              course_chroma_col = section['course_chroma_collection']
          }
        })

      })
      
      await read(element)
    }
    await read(component_state)
  }
}
