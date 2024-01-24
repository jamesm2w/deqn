BUILDDIR := build
PRODUCT := deqn

SRCDIR := src

HDRS := $(wildcard $(SRCDIR)/*.h)

CSRCS := $(wildcard $(SRCDIR)/*.C)
FSRCS += $(wildcard $(SRCDIR)/fortran/*.f90)

OBJS := $(CSRCS:$(SRCDIR)/%.C=$(BUILDDIR)/%.o)
OBJS += $(FSRCS:$(SRCDIR)/fortran/%.f90=$(BUILDDIR)/%.o)

BINARY := $(BUILDDIR)/$(PRODUCT)

# gcc flags:
CXX := g++
CXXFLAGS_DEBUG := -g -DDEBUG
CXXFLAGS_OPT := -O3
CXXFLAGS_OPENMP := -fopenmp

COZ_CXXFLAGS_DEBUG := $(CXXFLAGS_DEBUG)
COZ_CXXFLAGS_OPT := $(CXXFLAGS_OPT)
COZ_CXXFLAGS_OPENMP := $(CXXFLAGS_OPENMP)

COZ_CXXFLAGS := -g -gdwarf-3 -DCOZ $(COZ_CXXFLAGS_DEBUG) $(COZ_CXXFLAGS_OPT) $(CPPFLAGS)

LD := $(CXX)

# select optimized or debug
#CXXFLAGS := $(CXXFLAGS_OPT) $(CPPFLAGS)
CXXFLAGS := $(CXXFLAGS_OPT) $(CXXFLAGS_DEBUG) $(CPPFLAGS)

# add openmp flags (comment out for serial build)
CXXFLAGS += $(CXXFLAGS_OPENMP)
COZ_CXXFLAGS += $(COZ_CXXFLAGS_OPENMP)
LDFLAGS += $(CXXFLAGS_OPENMP)

all : $(BINARY)
	@echo $(COZ)

ifeq ($(COZ), true)

$(BINARY) : $(OBJS)
	@echo linking $@ w/ coz
	$(maketargetdir)
	$(LD) $(LDFLAGS) -ldl -o $@ $^

$(BUILDDIR)/%.o : $(SRCDIR)/%.C
	@echo compiling $< w/ coz
	$(maketargetdir)
	$(CXX) $(COZ_CXXFLAGS) $(CXXINCLUDES) -c -o $@ $<

else

$(BINARY) : $(OBJS)
	@echo linking $@
	$(maketargetdir)
	$(LD) $(LDFLAGS) -o $@ $^

$(BUILDDIR)/%.o : $(SRCDIR)/%.C
	@echo compiling $<
	$(maketargetdir)
	$(CXX) $(CXXFLAGS) $(CXXINCLUDES) -c -o $@ $<

endif

define maketargetdir
	-@mkdir -p $(dir $@) > /dev/null 2>&1
endef

clean :
	rm -f $(BINARY) $(OBJS)
	rm -rf $(BUILDDIR)
