#lang racket

(require 2htdp/image)


;; String -> [String Int [Int]]
(define (line->info s)
  (let ([tokens (string-split s)])
    (list (car tokens)
          (string->number (cadr tokens))
          (let ([ns (map string->number
                         (cddr tokens))])
            ns))))

(define root
  (build-path (find-system-path 'doc-dir) 
              "mysite" "static" "pools" "img"))

(define (extract-data)
  (call-with-input-file (build-path root "info.dat")
    (lambda (in) 
      (for/list ([line (in-lines in 'any)])
        (line->info line)))))

;; [Row] -> [ErrorMsg]
;; want to see ()
(define (validate rows)
  (filter string?
          (for/list ([row rows]
                     [n (in-naturals)])
            (cond 
              [(not (= (* 4 (cadr row))
                       (length (caddr row)))) 
               (format "numbers do not match in line ~a" n)]
              [(not (file-exists? (string->path (car row)))) 
               (format "~a does not exists in line ~a" (car row) n)]
              [else #t]))))


;; [Int] -> [[Int]]
(define (group-of-4s ns)
  (define (loop ns accm)
    (cond
      [(null? ns) accm]
      [(< (length ns) 4) (error "expected 4 elements")]
      [else (loop (drop ns 4)
                  (cons (take ns 4)
                        accm))]))
  (loop ns '()))

;; [Row] -> [Path [XYWH]]
(define (transform rows)
  (map (λ (row)
         (list (string->path (car row))
               (group-of-4s (caddr row))))
       rows))

;; Image Int Int Int Int -> Image
(define (mark img x y w h)
  (add-line
   (add-line
    (add-line 
     (add-line img
               x y (+ x w) y
               "white")
     (+ x w) y (+ x w) (+ y h)
     "white")
    (+ x w) (+ y h) x (+ y h)
    "white")
   x (+ y h) x y
   "white"))

;; Path [(x y w h)] -> [Image]
(define (mark-img path xywhs)
  (define (loop img xywhs)
    (if (null? xywhs)
        img
        (let ([x (car (car xywhs))]
              [y (cadr (car xywhs))]
              [w (caddr (car xywhs))]
              [h (cadddr (car xywhs))])
          (loop
           (mark img x y w h)
           (cdr xywhs)))))
  (loop (bitmap/file path) xywhs))

(module+ main
  
  (define rows
    (extract-data))
  
  ;; want to see ()
  (validate rows)
  
  ;; images with pools marked up
  (map (λ (row)
         (list (car row)
               (apply mark-img row)))
       (transform rows))
  
  ;; num of pools
  (define num-of-pools
  (apply +
         (map (λ (row)
                (cadr row))
              rows)))
  num-of-pools
  (* 0.8 num-of-pools)
  )




