import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {DataProviderService} from 'app/dataprovider.service';

@Component({
    selector: 'app-nsf-paper-nav',
    templateUrl: './nsf-paper-nav.component.html',
    styleUrls: ['./nsf-paper-nav.component.css']
})
export class NsfPaperNavComponent implements OnInit {
    @Output() updateContextRestriction: EventEmitter<any> = new EventEmitter();
    author_search_semnul_intrebarii: boolean = false
    request: string
    mode: string = 'content'
    canSend: boolean = false
    data: any = []
    loading: boolean = false
    loading_author: boolean = false
    all_authors: any = []
    displayed_authors: any = []
    full_screen: boolean = false
    author_input: string
    displayed_authors_stack: any = []
    show_back_button: boolean = false
    displayed_papers: any = []
    displayed_papers_author: any
    default_displayed_papers: any = []

    doc_restrictContext(document: any) {
        console.log("doc_restrictContext")
        console.log(document)
        this.full_screen = false
        this.updateContextRestriction.emit(document)
    }

    constructor(
        private dataProvider: DataProviderService) {
    }

    async ngOnInit() {
        let author_data = await this.dataProvider.nsfGetAllAuthors()
        this.all_authors = author_data["data"]
        this.displayed_authors = this.all_authors
    }

    set_mode(sm: string) {
        this.mode = sm
    }

    toggle_full_screen() {
        this.full_screen = !this.full_screen;
    }


    toggle_full_screen_authors() {
        this.full_screen = !this.full_screen;
        this.author_search_semnul_intrebarii = true;
        if (this.full_screen == true) {
            this.author_input = ''
            this.displayed_authors = this.all_authors;
        }
    }

    async toggle_full_screen_papers() {
        this.full_screen = !this.full_screen;
        this.author_search_semnul_intrebarii = false;
        if (this.full_screen == true) {
            this.author_input = ''
            await this.search_papers_default()
        }
    }

    async search_authors() {
        if (this.author_input.length <= 2) {
            this.displayed_authors = this.all_authors;
        } else {
            let author_data = await this.dataProvider.nsfGetAllAuthorsByName(this.author_input)
            this.displayed_authors = author_data["data"]
        }
    }


    async s_All(ev: any) {
        ev.preventDefault()
        if (this.author_search_semnul_intrebarii) {
            await this.search_authors()
        } else {
            await this.search_papers()
        }
    }

    async search_papers() {
        if (this.author_input.length <= 2) {
            // this.displayed_authors = this.all_authors;
            await this.search_papers_default()
        } else {

            let paper_data = await this.dataProvider.nsfGetAllPapersByName(this.author_input)
            this.displayed_authors = []
            this.displayed_papers = paper_data["data"].map((x: any) => {
                return {
                    metadata: {
                        info: {
                            paper: x
                        }
                    }
                }
            })
            console.log(this.displayed_papers)
            this.displayed_papers_author = {name: "Results for: `" + this.author_input + "`"}
            this.show_back_button = true

        }
    }

    async search_papers_default() {
        let paper_data = await this.dataProvider.nsfGetAllPapersByName('quantum')

        if (this.default_displayed_papers.length == 0) {
            this.displayed_papers = paper_data["data"].map((x: any) => {
                return {
                    metadata: {
                        info: {
                            paper: x
                        }
                    }
                }
            })
            this.default_displayed_papers = this.displayed_papers
        } else {
            this.displayed_papers = this.default_displayed_papers
        }


        console.log(this.displayed_papers)
        this.displayed_papers_author = {name: "Results for: `" + this.author_input + "`"}
        this.show_back_button = true
    }

    async get_author_papers(author_id: string) {
        console.log("author_id")
        console.log(author_id)
        this.displayed_authors_stack.push(this.displayed_authors)
        this.displayed_authors = this.all_authors.filter((x: any) => {
            return x["author_id"] == author_id
        })
        console.log(this.displayed_authors, this.all_authors)
        this.displayed_papers_author = this.displayed_authors[0]
        this.show_back_button = true
        this.loading_author = true
        let paper_data = await this.dataProvider.nsfGetPapersByAuthor({'author_id': author_id})
        console.log("PAPER DATA", paper_data)

        this.displayed_papers = []
        for (const [paper_id, paper] of Object.entries(paper_data["data"])) {
            this.displayed_papers.push({
                "result_id": paper_id,
                "metadata": {"info": paper}
            })
        }
        this.loading_author = false

        console.log(this.displayed_papers)
        // this.displayed_papers = paper_data['data']
    }

    paper_back() {
        this.show_back_button = false
        this.displayed_papers = []
        this.displayed_authors = this.displayed_authors_stack[this.displayed_authors.length - 1]
        this.displayed_authors_stack.pop()
    }

    async send() {
        this.loading = true
        let data = await this.dataProvider.nsfPaperRequest(this.request, this.mode)
        this.data = data
        this.loading = false
    }

    keyPressed(event: KeyboardEvent) {
        console.log(this.request)
        if ((this.request.length) > 1) {
            this.canSend = true;
        } else {
            this.canSend = false;
        }
        if (event.key === 'Enter') {
            this.send()
        }
    }
}
