# text_formatter
## Task from the Charles Weatherell's book Etudes for Programmers


Command list:

    ?size h,w
            -sets new page size, closes current page and starts a new one
    
    ?align fill|left|right|center|as_is
            -sets new paragraph alignment; closes current paragraph and starts 
             a new one

    ?par <space>,<indent>
            -sets paragraphs characteristics; closes current paragraph and
             starts a new one

    ?offset <left>,<right>
            -sets paragraphs characteristics; closes current paragraph and
             starts a new one

    ?interval <num>
            -sets space between lines; closes current paragraph and starts a
             new one

    ?feed <num>
            -adds <num> empty lines with intervals; closes current paragraph
             and starts a new one

    ?feed_lines <num>
            -adds <num> empty lines; closes current paragraph and starts a
             new one

    ?page_break
            -closes current paragraph and starts a new page

    ?left <num>
            -closes current paragraph; checks if <num> lines are left on page,
             then starts new page

    ?header <height>, <pos>, left|right|center|smart, top|bottom, header content
            -creates a header based on specifications
        
    ?p_num <num>, arabic|roman|letter, <prefix>
            -sets new page number

    ?br
            -closes current paragraph and starts a new one

    ?footnote <lines>
            -puts <lines> of text in a footnote

    ?alias <fictional>, <real>
            -changes a letter from <fictional> to <real> until next instance
             of ?alias without arguments
    
