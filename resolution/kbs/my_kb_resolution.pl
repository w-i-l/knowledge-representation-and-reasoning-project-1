[neg(student(X)), neg(course(C)), neg(enrolled(X, C)), completeAssignments(X, C)].
[neg(student(X)), neg(course(C)), neg(completeAssignments(X, C)), needsAccess(X, referenceBooks)].
[neg(canBorrow(X, referenceBooks)), hasLibraryCard(X)].
[neg(canBorrow(X, referenceBooks)), student(X)].
[neg(student(X)), hasLibraryCard(X)].
[student(john)].
[enrolled(john, ai)].
[course(ai)].

% Question
[neg(needsAccess(john, referenceBooks))].