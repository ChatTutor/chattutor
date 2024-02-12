import { Injectable, InjectionToken, Inject } from '@angular/core';
import { Message, asConversation } from './models/message.model';
import { ChatTutor } from './models/chattutor.model';

export const ENDPOINT_TOKEN = new InjectionToken<string>('endpoint');


@Injectable({
  providedIn: 'root'
})
export class ChatService {
  messages: Message[] = [];
  config: ChatTutor = {} as ChatTutor;
  constructor(@Inject(ENDPOINT_TOKEN) public endpoint: string) { }

  async sendMessage(message: Message, extra_collection?: string) {
    let convo = asConversation(this.messages)
    let args = {
      "conversation" : convo,
      "multiple" : true,
      "collection": [this.config.collection, extra_collection]
    }
    let response = await fetch(this.endpoint, {
      method: 'POST',
      body: JSON.stringify(args)
    })
    const reader = response.body?.getReader();
    return reader
  }
}
