;;hyde templates functions
(defun hyde-new-draft()
  "Init a new blog post for hyde engine"
  (interactive)
  (insert "{% extends \"_post.html\" %}\n{%hyde\n   title:\n    created:\n%}\n{% block article %}\n{% article %}\n\n{% endarticle %}\n{% endblock %}")
  (goto-line 8)
)