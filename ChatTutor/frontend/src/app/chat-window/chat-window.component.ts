import {Component, EventEmitter, HostBinding, HostListener, Input, OnInit, Output} from '@angular/core';
import {Paper} from 'app/models/paper.model';
import {DataMessage, Message} from "../models/message.model";
import {ChatTutor} from "../models/chattutor.model";
import { WStatus } from 'app/models/windowstatus.enum';

@Component({
    selector: 'app-chat-window',
    templateUrl: './chat-window.component.html',
    styleUrls: ['./chat-window.component.css']
})
export class ChatWindowComponent implements OnInit{
    messages: Message[] = []
    @Input() collections: string[] | undefined = ['test_embedding']
    @Input() restrictToDocument: any = undefined
    @Input() type: any
    @Input() openingMessage: string = `Hello, I am here to respond to any questions you might have about this chapter or course.\nFeel free to ask me anything!`
    documentInfo: any = undefined
    loadingFiles: boolean = false
    status: WStatus = WStatus.Idle
    endpoint: string = "/ask"

    pleaseStopGeneratingConvo: boolean = false

    ngOnInit(): void {
        this.messages.push({
            sender: "Assistant",
            content: formatMessage(this.openingMessage),
            role: 'assistant',
            timestamp: "0"
        } as Message);
    }

    setStatus(status: WStatus) {
        this.status = status
    }

    clearStatus() {
        this.status = WStatus.Idle
    }

    restrict(document: any) {
        this.restrictToDocument = document
    }

    stopGeneratingConvo() {
        this.pleaseStopGeneratingConvo = true
    }

    clearRestriction() {
        this.restrictToDocument = undefined
    }

    showInfo(document: any) {
        this.documentInfo = document
    }

    clearConversation() {
        this.messages = []
    }

    clearInfo() {
        if (this.documentInfo == this.restrictToDocument) {
            this.documentInfo = undefined
        }
        else {
            this.documentInfo = this.restrictToDocument
        }
    }

    async askChatTutor() {
        this.setStatus(WStatus.LoadingMessage)
        let args: ChatTutor = {
            conversation: this.messages,
            selectedModel: "gpt-3.5-turbo-16k",
            multiple: true,
        }

        if (this.collections) {
            args.collection = this.collections
        }

        if (this.restrictToDocument != undefined) {
            args.from_doc = this.restrictToDocument.metadata.doc
        }

        let req_init: RequestInit = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(args)
        }

        let response = await fetch(this.endpoint, req_init)
        return response
    }

    async addMessageToDB(message: Message) {
        let msg = message
        msg.time_created = msg.timestamp
        msg.chat_k = 'To set chat id'
        msg.clear_number = '0'
        const response = await fetch('addtodb', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(msg)})
    }

    async onSendMessage(messageText: string) {
        console.log("Updated message");
        const ms: Message = {
            sender: 'Student',
            timestamp: new Date().toLocaleTimeString(),
            role: 'user',
            content: messageText,
        }
        this.messages.push(ms);
        await this.addMessageToDB(ms)
        console.log(this.messages);
        console.log(JSON.stringify(this.messages))

        this.askForMessage().then(() => {
            console.log('Asked!')
        })
    }

    async askForMessage() {
        let response = await this.askChatTutor()

        let stop_gen = false
        let is_first = true
        let accumulated_content = ""
        let context_documents: any[]
        const reader = response.body!.getReader()
        let msg_in_progress: Message | undefined = undefined
        async function read(element: ChatWindowComponent): Promise<void> {
            //console.log(reader, "aaaa");
            let par = await reader.read()
            if (par.done) {
                stop_gen = false
                return
            }
            const string_value = new TextDecoder().decode(par.value)
            //console.log(string_value)

            const the_messages: DataMessage[] =
                string_value.split('\n\n')
                .filter(Boolean)
                .map(chunk => {
                    let spl = null
                    try {
                        spl = JSON.parse(chunk.split('data: ')[1]) }
                    catch (e) { spl = {}
                    }
                    return spl
                })
            for (let message_index in the_messages) {

                const message = the_messages[message_index]
                if (message == null)
                    continue
                if (message.message.valid_docs != undefined) {
                    context_documents = message.message.valid_docs
                }
                if (!stop_gen) {
                    const content_to_append = message.message.content
                    if (typeof (content_to_append) != 'undefined') {
                        accumulated_content += content_to_append
                    } else {
                        await element.addMessageToDB(msg_in_progress!)
                    }
                }
                if (is_first) {
                    // Add message to database
                    is_first = false

                    msg_in_progress = {
                        sender: 'Assistant',
                        timestamp: new Date().toLocaleTimeString(),
                        role: 'assistant',
                        content: formatMessage(accumulated_content),
                        valid_docs: context_documents,
                    }
                    console.log('msg', msg_in_progress);
                    element.messages.push(msg_in_progress)
                } else {
                    const ind = element.messages.length
                    element.messages[ind - 1].content = formatMessage(accumulated_content)
                    msg_in_progress = element.messages[ind - 1]
                }
                if (stop_gen) {
                    accumulated_content += ' ...Stopped generating';
                }
            }
            if (!stop_gen) {
                read(element);
            } else {

            }
        }
        console.log("Messages", this.messages);

        this.setStatus(WStatus.GeneratingMessage)
        await read(this)
        this.clearStatus()
        console.log("Messages", this.messages);

        //console.log('Reader', reader);
    }

    @HostBinding('style.border') private borderStyle = '0px solid';
    @HostBinding('style.border-color') private borderColor = '#696D7D';
    @HostBinding('style.border-radius') private borderRadius = '0px';

    filesArray: Array<File> = []
    urlsArray: Array<string> = []

    @HostListener('dragover', ['$event'])
    public onDragOver(evt: DragEvent) {
        this.setStatus(WStatus.DragOver)
        evt.preventDefault()
        evt.stopPropagation()
    }

    @HostListener('dragleave', ['$event'])
    public onDragLeave(evt: DragEvent) {
        evt.preventDefault();
        evt.stopPropagation();
        this.clearStatus()
    }

    @HostListener('drop', ['$event'])
    public async onDrop(evt: DragEvent) {
        this.clearStatus()
        evt.preventDefault();
        evt.stopPropagation();
        let files = evt.dataTransfer!.files;
        let valid_files: Array<File> = Array.from(files);
        this.loadingFiles = true
        const response = await this.sendFilesToBackend(valid_files,
            `files_collection`);
        console.log('response:', response)
        this.loadingFiles = false
    }

    async sendFilesToBackend(files: Array<File>, collection_name: string) {
        this.setStatus(WStatus.UploadingContent)
        let form_data = new FormData()
        form_data.append('collection_name', collection_name)
        for (const ind in files) {
            form_data.append('file', files[ind])
        }
        const response = await fetch('/upload_data_from_drop', {
            method: 'POST',
            headers: {'Accept': 'multipart/form-data'},
            body: form_data
        })
        const coll = await response.json()
        if(coll['message'] == 'error') {
            this.setStatus(WStatus.UploadedContent)
            return {message: 'error'}
        }
        if (!this.collections?.includes('files_collection')) {
            this.collections?.push('files_collection')
        }
        this.filesArray = [...this.filesArray, ...coll['files_uploaded_name']]
        this.setStatus(WStatus.UploadedContent)
        return {message: 'success', json_obj: coll}
    }

    async sendURLsToBackend(urls: Array<string>, collection_name: string) {
        this.setStatus(WStatus.UploadingContent)
        let data_ = {url: urls, name: collection_name}
        let response = await fetch('/upload_site_url', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data_)
        })
        let res_json = await response.json()
        console.log('Res_json', res_json)
        if(res_json['message'] == 'error') {
            this.setStatus(WStatus.UploadedContent)
            return {message: 'failure'}
        }
        if (!this.collections?.includes('files_collection')) {
            this.collections?.push('files_collection')
        }

        this.urlsArray = [...this.urlsArray, ...res_json['urls']]
        this.setStatus(WStatus.UploadedContent)

        return {message: 'success', json_obj: res_json}
    }
    
    readonly WStatus = WStatus
}


function formatMessage(message: string, makeLists: boolean = true) {
    const messageArr = message.split("\n")
  
    let messageStr = ""
    let listSwitch = 0
    for (let messageArrIndex in messageArr) {
      const paragraph = messageArr[messageArrIndex]
      if(paragraph.startsWith('- ') && makeLists) {
        if(listSwitch === 0) {
          messageStr += "<ul style=\"padding-left: 15px !important;\">"
        }
  
        messageStr += `<li><p>${paragraph.slice(2)}</p></li>`
  
        listSwitch = 1
  
      } else if (listSwitch === 1) {
        messageStr += "</ul>"
        messageStr += `<p>${paragraph}</p>`
        listSwitch = 0
      } else {
        messageStr += `<p>${paragraph}</p>`
        listSwitch = 0
      }
  
    }
    return messageStr
  }
  
