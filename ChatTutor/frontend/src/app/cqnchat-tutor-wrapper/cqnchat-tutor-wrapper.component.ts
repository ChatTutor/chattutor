import { Component, ViewChild } from '@angular/core';
import { ChatWindowComponent } from 'app/chat-window/chat-window.component';

@Component({
  selector: 'app-cqnchat-tutor-wrapper',
  templateUrl: './cqnchat-tutor-wrapper.component.html',
  styleUrls: ['./cqnchat-tutor-wrapper.component.css']
})
export class CQNChatTutorWrapperComponent {
  @ViewChild(ChatWindowComponent ) child: ChatWindowComponent;
    restrict(document: any) {
      console.log("event@")
      console.log(document)
      document["metadata"]["doc"] = document["metadata"]["info"]["paper"]["chroma_doc_id"]

      if (document["metadata"]["doc"] == undefined)
        document["metadata"]["doc"] = document["metadata"]["info"]["paper"]["result_id"]

      this.child.restrict(document)
  }
}
