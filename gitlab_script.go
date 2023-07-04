package main

import (
	"fmt"
	"log"
	"os"

	gitlab "github.com/xanzy/go-gitlab"
)

func main() {
	git := gitlab.NewClient(nil, os.Getenv("GITLAB_TOKEN"))

	opt := &gitlab.ListProjectsOptions{
		ListOptions: gitlab.ListOptions{
			PerPage: 10,
			Page:    1,
		},
	}

	for {
		projects, resp, err := git.Projects.ListProjects(opt)
		if err != nil {
			log.Fatal(err)
		}

		for _, p := range projects {
			fmt.Printf("ID: %d, Name: %s, Description: %s, SSH URL: %s, Web URL: %s\n",
				p.ID, p.Name, p.Description, p.SSHURLToRepo, p.WebURL)
		}

		if resp.CurrentPage >= resp.TotalPages {
			break
		}

		opt.Page = resp.NextPage
	}
}
