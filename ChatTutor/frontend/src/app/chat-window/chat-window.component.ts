import { Component } from '@angular/core';
import { Paper } from 'app/models/paper.model';
import {DataMessage, Message} from "../models/message.model";
import {ChatTutor} from "../models/chattutor.model";
@Component({
  selector: 'app-chat-window',
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.css']
})
export class ChatWindowComponent {
  messages: Message[] = [];
  
  onSendMessage(messageText: string) {
    this.messages.push({
        sender: 'Student',
        timestamp: new Date().toLocaleTimeString(),
        role: 'user',
        content: messageText,
    });
    this.askForMessage().then(() => {
        console.log('Asked!')
    })
  }

  async askForMessage() {
      let args: ChatTutor = {
          conversation: this.messages,
          selectedModel: "gpt-3.5-turbo-16k",
          multiple: true,
          collection: ['test_embedding']
      }

      let req_init: RequestInit = {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(args)
      }

      console.log(args);
      let stop_gen = false
      let response = await fetch('/ask', req_init)
      let is_first = true
      let accumulated_content = ""
      let context_documents: any[]
      const reader = response.body!.getReader()
      function read(element: ChatWindowComponent): void {
          console.log(reader, "aaaa");
          reader.read().then((par) => {
              if (par.done) {
                  stop_gen = false
                  return
              }
              const string_value = new TextDecoder().decode(par.value)
              console.log(string_value)

              const the_messages: DataMessage[] = string_value.split('\n\n').filter(Boolean).map(chunk => JSON.parse(chunk.split('data: ')[1]))
              for (let message_index in the_messages) {

                  const message = the_messages[message_index]
                  if(message.message.valid_docs != undefined) {
                        context_documents = message.message.valid_docs
                  }
                  if (!stop_gen) {
                      const content_to_append = message.message.content
                      if(typeof(content_to_append) != 'undefined') {
                          accumulated_content += content_to_append
                      } else {
                          console.log('Uploaded message')
                      }
                  }
                  if (is_first) {
                      // Add message to database
                      is_first = false

                      let msg_in_progress: Message = {
                              sender: 'Assistant',
                              timestamp: new Date().toLocaleTimeString(),
                              role: 'assistant',
                              content: accumulated_content,
                                valid_docs: context_documents,
                          }
                          console.log('msg', msg_in_progress);
                      element.messages.push(msg_in_progress)
                  } else {
                      const ind = element.messages.length
                      element.messages[ind - 1].content = accumulated_content
                  }
                  if (stop_gen) {
                      accumulated_content += ' ...Stopped generating';
                  }
              }
              if(!stop_gen) {
                  read(element);
              } else {

              }
          })
      }
      read(this)
      console.log(this.messages);
      console.log('Reader', reader);
  }
}
