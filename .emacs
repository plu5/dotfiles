;;(require 'package)
;;(package-activate 'use-package)
;; (add-to-list 'package-archives '("gnu"   . "https://elpa.gnu.org/packages/"))
;; (add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/"))
;; (package-initialize)
;; (unless (package-installed-p 'use-package)
;;   (package-refresh-contents)
;;   (package-install 'use-package))
;; (eval-and-compile
;;   (setq use-package-always-ensure t
;;         use-package-expand-minimally t))
;; (require 'use-package)
(add-to-list 'custom-theme-load-path "/media/pnotes/emacs")
(add-to-list 'load-path "/media/Windows/Users/pm/dev/reps/emacs-doentry")
(add-to-list 'load-path "/media/pnotes/emacs")
(setq auto-save-default nil)
(require 'pm)

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(auth-source-save-behavior nil)
 '(ignored-local-variable-values '((projectile-project-name . "notes")))
 '(inhibit-startup-screen t)
 '(package-selected-packages
   '(expand-region yasnippet magit evil multiple-cursors avy flycheck noflet ws-butler undo-tree smex move-text imenu-list ido-grid-mode ido-completing-read+ diminish anzu))
 '(safe-local-variable-values '((projectile-project-name . "notes"))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

;; startup frames configuration
(find-file p-main-file)
(add-hook 'after-make-frame-functions
          (lambda (frame)
            (select-frame frame)
            (cond
             ((equal (frame-parameter frame 'name) "2nd - GNU Emacs at pos")
              (find-file p-main-file)))))
(make-frame '((name . "2nd - GNU Emacs at pos")))
(make-frame)
;; (setq default-frame-alist '((font . "SourceCodePro 13")))
