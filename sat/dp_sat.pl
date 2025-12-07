% neg(neg(L), L) :- !.
% neg(L, neg(L)).

% get_atom(neg(A), A) :- !.
% get_atom(A, A).

% bullet_op([], _, []).
% bullet_op([Clause|Rest], Lit, Result) :-
%     neg(Lit, NegLit),
%     (   
%         member(Lit, Clause) ->
%         bullet_op(Rest, Lit, Result) ;
%         member(NegLit, Clause) ->
%             select(NegLit, Clause, Reduced),
%             bullet_op(Rest, Lit, RestResult),
%             Result = [Reduced|RestResult] ;
%             bullet_op(Rest, Lit, RestResult),
%             Result = [Clause|RestResult]
%     ).

% collect_all_atoms([], []).
% collect_all_atoms([Clause|Rest], Atoms) :-
%     maplist(get_atom, Clause, ClauseAtoms),
%     collect_all_atoms(Rest, RestAtoms),
%     append(ClauseAtoms, RestAtoms, AllAtoms),
%     list_to_set(AllAtoms, Atoms).

% count_positive_negative([], _, 0, 0).
% count_positive_negative([Clause|Rest], Atom, Pos, Neg) :-
%     count_positive_negative(Rest, Atom, RestPos, RestNeg),
%     (   
%         member(Atom, Clause) ->
%             Pos is RestPos + 1,
%             Neg = RestNeg ;
%             member(neg(Atom), Clause) ->
%                 Pos = RestPos,
%                 Neg is RestNeg + 1 ;
%                 Pos = RestPos,
%                 Neg = RestNeg
%     ).

% balance_score(Atom, Clauses, Score) :-
%     count_positive_negative(Clauses, Atom, Pos, Neg),
%     Score is abs(Pos - Neg).

% select_atom_most_balanced(Clauses, BestAtom) :-
%     collect_all_atoms(Clauses, AllAtoms),
%     AllAtoms = [FirstAtom|RestAtoms],
%     balance_score(FirstAtom, Clauses, FirstScore),
%     find_most_balanced(RestAtoms, Clauses, FirstAtom, FirstScore, BestAtom).

% find_most_balanced([], _, BestAtom, _, BestAtom).
% find_most_balanced([Atom|Rest], Clauses, CurrentBest, CurrentScore, BestAtom) :-
%     balance_score(Atom, Clauses, Score),
%     (   
%         Score < CurrentScore ->
%             find_most_balanced(Rest, Clauses, Atom, Score, BestAtom) ;
%             find_most_balanced(Rest, Clauses, CurrentBest, CurrentScore, BestAtom)
%     ).

% find_shortest_clause(Clauses, ShortestLength) :-
%     maplist(length, Clauses, Lengths),
%     min_list(Lengths, ShortestLength).

% atom_in_shortest_clause(Atom, Clauses) :-
%     find_shortest_clause(Clauses, MinLen),
%     member(Clause, Clauses),
%     length(Clause, MinLen),
%     member(Lit, Clause),
%     get_atom(Lit, Atom),
%     !.

% select_atom_shortest_clause(Clauses, Atom) :-
%     atom_in_shortest_clause(Atom, Clauses).

% dp_solve(_, [], yes([]), 1).
% dp_solve(_, Clauses, no, 1) :-
%     member([], Clauses),
%     !.
% dp_solve(Strategy, Clauses, Result, Steps) :-
%     call(Strategy, Clauses, Atom),
%     bullet_op(Clauses, Atom, C1),
%     dp_solve(Strategy, C1, Result1, Steps1),
%     (   
%         Result1 = yes(Model1) ->
%             Result = yes([Atom/true|Model1]),
%             Steps is Steps1 + 1 ;
%             neg(Atom, NegAtom),
%             bullet_op(Clauses, NegAtom, C2),
%             dp_solve(Strategy, C2, Result2, Steps2),
%             (   
%                 Result2 = yes(Model2) ->
%                     Result = yes([Atom/false|Model2]),
%                     Steps is Steps1 + Steps2 + 1 ;
%                     Result = no,
%                     Steps is Steps1 + Steps2 + 1
%             )
%     ),
%     !.

% davis_putnam(Clauses, Strategy, Result, Steps) :-
%     dp_solve(Strategy, Clauses, Result, Steps).

% % % % % % % % % % % % % % 
% read_kb_from_file(FileName, Clauses) :-
%     open(FileName, read, Stream),
%     read_clauses_from_stream(Stream, Clauses),
%     close(Stream).

% read_clauses_from_stream(Stream, []) :-
%     at_end_of_stream(Stream), !.

% read_clauses_from_stream(Stream, [Clause|Rest]) :-
%     \+ at_end_of_stream(Stream),
%     read_term(Stream, Clause, []),
%     Clause \= end_of_file,
%     read_clauses_from_stream(Stream, Rest).

% run_dp_file(FileName, Strategy, Result, Steps) :-
%     read_kb_from_file(FileName, Clauses),
%     davis_putnam(Clauses, Strategy, Result, Steps).


neg(neg(L), L) :- !.
neg(L, neg(L)).

get_atom(neg(A), A) :- !.
get_atom(A, A).

bullet_op([], _, []).
bullet_op([Clause|Rest], Lit, Result) :-
    neg(Lit, NegLit),
    (   
        member(Lit, Clause) ->
        bullet_op(Rest, Lit, Result) ;
        member(NegLit, Clause) ->
            select(NegLit, Clause, Reduced),
            bullet_op(Rest, Lit, RestResult),
            Result = [Reduced|RestResult] ;
            bullet_op(Rest, Lit, RestResult),
            Result = [Clause|RestResult]
    ).

collect_all_atoms([], []).
collect_all_atoms([Clause|Rest], Atoms) :-
    maplist(get_atom, Clause, ClauseAtoms),
    collect_all_atoms(Rest, RestAtoms),
    append(ClauseAtoms, RestAtoms, AllAtoms),
    list_to_set(AllAtoms, Atoms).

count_positive_negative([], _, 0, 0).
count_positive_negative([Clause|Rest], Atom, Pos, Neg) :-
    count_positive_negative(Rest, Atom, RestPos, RestNeg),
    (   
        member(Atom, Clause) ->
            Pos is RestPos + 1,
            Neg = RestNeg ;
            member(neg(Atom), Clause) ->
                Pos = RestPos,
                Neg is RestNeg + 1 ;
                Pos = RestPos,
                Neg = RestNeg
    ).

balance_score(Atom, Clauses, Score) :-
    count_positive_negative(Clauses, Atom, Pos, Neg),
    Score is abs(Pos - Neg).

select_atom_most_balanced(Clauses, BestAtom) :-
    collect_all_atoms(Clauses, AllAtoms),
    AllAtoms = [FirstAtom|RestAtoms],
    balance_score(FirstAtom, Clauses, FirstScore),
    find_most_balanced(RestAtoms, Clauses, FirstAtom, FirstScore, BestAtom).

find_most_balanced([], _, BestAtom, _, BestAtom).
find_most_balanced([Atom|Rest], Clauses, CurrentBest, CurrentScore, BestAtom) :-
    balance_score(Atom, Clauses, Score),
    (   
        Score < CurrentScore ->
            find_most_balanced(Rest, Clauses, Atom, Score, BestAtom) ;
            find_most_balanced(Rest, Clauses, CurrentBest, CurrentScore, BestAtom)
    ).

find_shortest_clause(Clauses, ShortestLength) :-
    maplist(length, Clauses, Lengths),
    min_list(Lengths, ShortestLength).

atom_in_shortest_clause(Atom, Clauses) :-
    find_shortest_clause(Clauses, MinLen),
    member(Clause, Clauses),
    length(Clause, MinLen),
    member(Lit, Clause),
    get_atom(Lit, Atom),
    !.

select_atom_shortest_clause(Clauses, Atom) :-
    atom_in_shortest_clause(Atom, Clauses).

dp_solve(_, [], yes([]), 1).
dp_solve(_, Clauses, no, 1) :-
    member([], Clauses),
    !.
dp_solve(Strategy, Clauses, Result, TotalSteps) :-
    call(Strategy, Clauses, Atom),
    (
        (
            bullet_op(Clauses, Atom, C1),
            dp_solve(Strategy, C1, SubResult, Steps1),
            SubResult = yes(Model)
        ) ->
        Result = yes([Atom/true|Model]),
        TotalSteps is Steps1 + 1
    ;
        (
            neg(Atom, NegAtom),
            bullet_op(Clauses, NegAtom, C2),
            dp_solve(Strategy, C2, SubResult, Steps2),
            SubResult = yes(Model)
        ) ->
        Result = yes([Atom/false|Model]),
        TotalSteps is Steps2 + 1
    ;
        Result = no,
        TotalSteps is 1
    ).

davis_putnam(Clauses, Strategy, Result, Steps) :-
    dp_solve(Strategy, Clauses, Result, Steps).


% % % % % % % % % % % % % 

format_result(no, 'UNSAT', '').
format_result(yes(Model), 'SAT', ModelStr) :-
    format_model(Model, ModelStr).

format_model([], '').
format_model([Atom/Value|Rest], Str) :-
    format_model(Rest, RestStr),
    (Value = true -> ValStr = 'true' ; ValStr = 'false'),
    atom_string(Atom, AtomStr),
    (RestStr = '' -> 
        format(string(Str), '~w/~w', [AtomStr, ValStr])
    ;
        format(string(Str), '~w/~w, ~w', [AtomStr, ValStr, RestStr])
    ).

run_dp_file_formatted(FileName, Strategy, ResultType, ModelStr, Steps) :-
    read_kb_from_file(FileName, Clauses),
    davis_putnam(Clauses, Strategy, Result, Steps),
    format_result(Result, ResultType, ModelStr).

read_kb_from_file(FileName, Clauses) :-
    open(FileName, read, Stream),
    read_clauses_from_stream(Stream, Clauses),
    close(Stream).

read_clauses_from_stream(Stream, []) :-
    at_end_of_stream(Stream), !.

read_clauses_from_stream(Stream, [Clause|Rest]) :-
    \+ at_end_of_stream(Stream),
    read_term(Stream, Clause, []),
    Clause \= end_of_file,
    read_clauses_from_stream(Stream, Rest).

run_dp_file(FileName, Strategy, Result, Steps) :-
    read_kb_from_file(FileName, Clauses),
    davis_putnam(Clauses, Strategy, Result, Steps).